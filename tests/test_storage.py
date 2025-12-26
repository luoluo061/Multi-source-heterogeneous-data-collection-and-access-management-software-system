from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base
from app.storage.raw_storage import persist_raw_records


def test_persist_raw_records():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()

    stored = persist_raw_records(
        session,
        run_id="test-run",
        source_id=1,
        items=[
            {
                "payload": b"sample",
                "format": "TEXT",
                "raw_size": 6,
                "validation_status": "PASSED",
                "validation_message": "OK",
            }
        ],
    )

    assert len(stored) == 1
    assert stored[0].checksum is not None
