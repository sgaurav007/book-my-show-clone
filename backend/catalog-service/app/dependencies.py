from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from redis.asyncio import Redis

from app.config import settings
from app.repositories import MovieRepository, TheaterRepository, ShowRepository, SeatRepository
from app.services import MovieService, TheaterService, ShowService, SeatService

# Database engine and session
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Redis connection
_redis_client: Optional[Redis] = None


async def get_redis() -> Optional[Redis]:
    """Get Redis client"""
    global _redis_client
    
    if not settings.redis_enabled:
        return None
    
    if _redis_client is None:
        _redis_client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True,
        )
    
    return _redis_client


async def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_movie_service(db: AsyncSession = None) -> MovieService:
    """Get MovieService instance"""
    if db is None:
        async for session in get_db():
            db = session
            break
    
    redis = await get_redis()
    repository = MovieRepository(db)
    return MovieService(repository, redis)


async def get_theater_service(db: AsyncSession = None) -> TheaterService:
    """Get TheaterService instance"""
    if db is None:
        async for session in get_db():
            db = session
            break
    
    redis = await get_redis()
    repository = TheaterRepository(db)
    return TheaterService(repository, redis)


async def get_show_service(db: AsyncSession = None) -> ShowService:
    """Get ShowService instance"""
    if db is None:
        async for session in get_db():
            db = session
            break
    
    repository = ShowRepository(db)
    movie_repository = MovieRepository(db)
    seat_repository = SeatRepository(db)
    return ShowService(repository, movie_repository, seat_repository)


async def get_seat_service(db: AsyncSession = None) -> SeatService:
    """Get SeatService instance"""
    if db is None:
        async for session in get_db():
            db = session
            break
    
    repository = SeatRepository(db)
    return SeatService(repository)
