import csv
import io
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.merchants import Merchants
from ...models.user import User
from ...models.user_merchants import UserMerchants
from ...schemas.util import Role

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

REQUIRED_COLUMNS = {
    "name",
    "external_ref",
    "currency",
}

BATCH_SIZE = 1000


class MerchantSetupRepository:

    @staticmethod
    async def import_merchants_from_csv(
        session: AsyncSession,
        *,
        file: UploadFile,
    ) -> dict:

        # -----------------------------------------
        # 1. Read CSV file
        # -----------------------------------------

        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="CSV file exceeds the 5 MB limit.",
            )

        try:
            csv_content = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="CSV must be UTF-8 encoded.",
            )

        reader = csv.DictReader(io.StringIO(csv_content))

        if not reader.fieldnames:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty.",
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
                    "message": "Missing required CSV columns.",
                    "missing_columns": sorted(missing_columns),
                },
            )

        # -----------------------------------------
        # 2. Prepare merchant records
        # -----------------------------------------

        merchant_records = []

        for row in reader:

            if not any((value or "").strip() for value in row.values()):
                continue

            name = (row.get("name") or "").strip()
            external_ref = (row.get("external_ref") or "").strip()
            currency = (row.get("currency") or "").strip().upper()

            if not name or not external_ref or not currency:
                raise HTTPException(
                    status_code=422,
                    detail="Merchant name, external_ref and currency are required.",
                )

            if len(name) > 255 or len(external_ref) > 100:
                raise HTTPException(
                    status_code=422,
                    detail="Merchant name or external_ref exceeds its column limit.",
                )

            if len(currency) != 3 or not currency.isalpha():
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid currency for merchant: {name}",
                )

            merchant_records.append({
                "name": name,
                "external_ref": external_ref,
                "currency": currency,
            })

        if not merchant_records:
            raise HTTPException(
                status_code=400,
                detail="No merchant records found in CSV.",
            )

        # -----------------------------------------
        # 3. Insert merchants
        # -----------------------------------------

        merchant_statement = (
            insert(Merchants)
            .values(merchant_records)
            .on_conflict_do_nothing(
                constraint="uq_merchants_external_ref"
            )
            .returning(Merchants.id)
        )

        inserted_merchant_ids = (
            await session.scalars(merchant_statement)
        ).all()

        # -----------------------------------------
        # 4. Retrieve ALL merchants
        # -----------------------------------------

        # This ensures every existing user gets access
        # to every merchant, including merchants that
        # were already present in the database.

        merchant_result = await session.scalars(
            select(Merchants.id)
        )

        merchant_ids = merchant_result.all()

        # -----------------------------------------
        # 5. Retrieve all existing users
        # -----------------------------------------

        user_result = await session.scalars(
            select(User.id)
        )

        user_ids = user_result.all()

        # -----------------------------------------
        # 6. Create user-merchant associations
        # -----------------------------------------

        associations = [
            {
                "user_id": user_id,
                "merchant_id": merchant_id,
                "role": Role.ANALYST.value,
            }
            for user_id in user_ids
            for merchant_id in merchant_ids
        ]

        associations_inserted = 0

        # Insert in batches to avoid an excessively
        # large SQL INSERT statement.

        for start in range(0, len(associations), BATCH_SIZE):

            batch = associations[start:start + BATCH_SIZE]

            association_statement = (
                insert(UserMerchants)
                .values(batch)
                .on_conflict_do_nothing(
                    index_elements=[
                        UserMerchants.user_id,
                        UserMerchants.merchant_id,
                    ]
                )
                .returning(UserMerchants.user_id)
            )

            inserted = (
                await session.scalars(association_statement)
            ).all()

            associations_inserted += len(inserted)

        await session.flush()

        return {
            "merchants_inserted": len(inserted_merchant_ids),
            "total_merchants": len(merchant_ids),
            "users_found": len(user_ids),
            "associations_inserted": associations_inserted,
        }

    # -------------------------------------------------
    # Add a newly registered user to all merchants
    # -------------------------------------------------

    @staticmethod
    async def add_user_to_all_merchants(
        session: AsyncSession,
        *,
        user_id: UUID,
    ) -> int:

        merchant_result = await session.scalars(
            select(Merchants.id)
        )

        merchant_ids = merchant_result.all()

        if not merchant_ids:
            return 0

        associations = [
            {
                "user_id": user_id,
                "merchant_id": merchant_id
            }
            for merchant_id in merchant_ids
        ]

        statement = (
            insert(UserMerchants)
            .values(associations)
            .on_conflict_do_nothing(
                index_elements=[
                    UserMerchants.user_id,
                    UserMerchants.merchant_id,
                ]
            )
            .returning(UserMerchants.user_id)
        )

        inserted = (await session.scalars(statement)).all()

        return len(inserted)