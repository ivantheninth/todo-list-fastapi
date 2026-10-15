from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.oauth_identity import OAuthIdentity
from app.db.models.user import User
from app.crud.user import user_crud


class OAuthEmailAlreadyExistsError(Exception):
    pass


class OAuthIdentityAlreadyExistsError(Exception):
    pass


class OAuthIdentityCreationConflictError(Exception):
    pass


class OAuthIdentityCrud:

    async def get_by_provider_and_provider_user_id(
        self,
        session: AsyncSession,
        provider: str,
        provider_user_id: str,
    ) -> OAuthIdentity | None:
        stmt = select(OAuthIdentity).where(
            OAuthIdentity.provider == provider,
            OAuthIdentity.provider_user_id == provider_user_id,
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def create_user_with_identity(
        self,
        session: AsyncSession,
        username: str,
        verified_email: str,
        provider: str,
        verified_provider_user_id: str,
    ) -> OAuthIdentity:
        """Create an OAuth-only account from provider claims verified upstream."""
        existing_user = await user_crud.get_user_by_email(
            session,
            verified_email,
        )
        if existing_user is not None:
            raise OAuthEmailAlreadyExistsError

        existing_identity = await self.get_by_provider_and_provider_user_id(
            session=session,
            provider=provider,
            provider_user_id=verified_provider_user_id,
        )
        if existing_identity is not None:
            raise OAuthIdentityAlreadyExistsError

        user = User(
            username=username,
            email=verified_email,
            hashed_password=None,
        )
        identity = OAuthIdentity(
            user=user,
            provider=provider,
            provider_user_id=verified_provider_user_id,
        )

        try:
            async with session.begin_nested():
                session.add(identity)
                await session.flush()
        except IntegrityError as exc:
            if getattr(exc.orig, "sqlstate", None) == "23505":
                raise OAuthIdentityCreationConflictError from exc
            raise

        return identity


oauth_identity_crud = OAuthIdentityCrud()
