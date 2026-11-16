import csv
import io
from uuid import UUID

from fastapi import HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.financial_transactions import FinancialTransactions
from ...schemas.transaction import TransactionCSVRow
from ...schemas.util import Status

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_ROWS = 10_000
BATCH_SIZE = 500

REQUIRED_COLUMNS = {
    "provider",
    "provider_payment_id",
    "amount",
    "currency",
    "status",
    "payment_method",
}

STATUS_ALIASES = {
    "SUCCESS": ("SUCCESS", "SUCCEEDED", "COMPLETED"),
    "FAILED": ("FAILED", "FAILURE", "DECLINED"),
    "PENDING": ("PENDING", "PROCESSING", "QUEUED"),
    "QUEUED": ("QUEUED", "PENDING", "PROCESSING"),
}


def resolve_status(raw_status: str) -> str:
    """
    Resolve a CSV status label to a value supported by
    the application's Status enum.
    """

    normalized = raw_status.strip().upper()

    candidates = STATUS_ALIASES.get(
        normalized,
        (normalized,),
    )

    for candidate in candidates:

        # Match the enum member name.
        member = Status.__members__.get(candidate)

        if member is not None:
            return str(member.value)

        # Match the enum member value.
        for member in Status:
            if str(member.value).upper() == candidate:
                return str(member.value)

    raise ValueError(
        f"Unsupported transaction status: {raw_status}"
    )


def parse_transaction_row(data: dict) -> dict:

    validated = TransactionCSVRow.model_validate(data)

    result = validated.model_dump()

    result["status"] = resolve_status(result["status"])

    result["provider"] = result["provider"].lower()
    result["payment_method"] = result["payment_method"].lower()

    if result["failure_code"]:
        result["failure_code"] = result["failure_code"].upper()

    return result


async def import_transactions_csv(
    session: AsyncSession,
    *,
    merchant_id: UUID,
    file: UploadFile,
) -> dict:

    # 1. Read and validate file size.
    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="CSV file exceeds the 10 MB limit.",
        )

    # 2. Decode CSV.
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV must be UTF-8 encoded.",
        )

    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail="CSV file is empty or has no header.",
        )

    if len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise HTTPException(
            status_code=400,
            detail="CSV contains duplicate column names.",
        )

    missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "CSV is missing required columns.",
                "missing_columns": sorted(missing_columns),
            },
        )

    # 3. Validate all rows before inserting anything.
    valid_records = []
    errors = []
    total_rows = 0

    for row_number, raw_row in enumerate(reader, start=2):

        if not any((value or "").strip() for value in raw_row.values()):
            continue

        total_rows += 1

        if total_rows > MAX_ROWS:
            raise HTTPException(
                status_code=413,
                detail=f"CSV cannot contain more than {MAX_ROWS} records.",
            )

        # Never trust merchant_id supplied by the CSV.
        # The authorized merchant_id comes from the API request.
        row_data = {
            key: (value or "").strip()
            for key, value in raw_row.items()
            if key != "merchant_id"
        }

        try:
            transaction = parse_transaction_row(row_data)

            transaction["merchant_id"] = merchant_id

            valid_records.append(transaction)

        except (ValidationError, ValueError) as exc:

            errors.append({
                "row": row_number,
                "error": str(exc),
            })

    # All-or-nothing validation: no partial import.
    if errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "CSV validation failed. No records were imported.",
                "total_errors": len(errors),
                "errors": errors[:20],
            },
        )

    if not valid_records:
        raise HTTPException(
            status_code=400,
            detail="CSV contains no transaction records.",
        )

    # 4. Bulk insert in batches.
    inserted_count = 0

    try:
        for start in range(0, len(valid_records), BATCH_SIZE):

            batch = valid_records[
                start : start + BATCH_SIZE
            ]

            statement = (
                insert(FinancialTransactions)
                .values(batch)
                .on_conflict_do_nothing(
                    constraint="uq_financial_transactions_provider_payment"
                )
                .returning(FinancialTransactions.id)
            )

            result = await session.execute(statement)

            inserted_ids = result.scalars().all()

            inserted_count += len(inserted_ids)

    except Exception:
        await session.rollback()
        raise

    return {
        "total_valid_rows": len(valid_records),
        "inserted": inserted_count,
        "skipped_duplicates": len(valid_records) - inserted_count,
    }