from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.cloud_models import DiseaseSymptomEdge
from app.schemas.diagnostic import RankedDisease
from app.services.disease_symptom_graph import DiseaseSymptomGraph


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    DiseaseSymptomEdge.__table__.create(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_edges_for_returns_edges_for_candidate_disease_names() -> None:
    db = _session()
    db.add_all(
        [
            DiseaseSymptomEdge(
                disease_id="Cúm mùa",
                symptom="sốt",
                weight=0.8,
                is_discriminative=True,
            ),
            DiseaseSymptomEdge(
                disease_id="Cúm mùa",
                symptom="đau họng",
                weight=0.5,
                is_discriminative=False,
            ),
            DiseaseSymptomEdge(
                disease_id="Viêm phổi",
                symptom="khó thở",
                weight=0.9,
                is_discriminative=True,
            ),
            DiseaseSymptomEdge(
                disease_id="Không liên quan",
                symptom="đau bụng",
                weight=0.3,
                is_discriminative=False,
            ),
        ]
    )
    db.commit()

    graph = DiseaseSymptomGraph(db)
    edges = graph.edges_for(
        [
            RankedDisease(name="Cúm mùa", probability=0.6),
            RankedDisease(name="Viêm phổi", probability=0.4),
        ]
    )

    assert [(edge.disease_id, edge.symptom) for edge in edges] == [
        ("Cúm mùa", "sốt"),
        ("Cúm mùa", "đau họng"),
        ("Viêm phổi", "khó thở"),
    ]


def test_edges_for_empty_candidates_or_empty_result_returns_empty_list() -> None:
    db = _session()
    graph = DiseaseSymptomGraph(db)

    assert graph.edges_for([]) == []
    assert graph.edges_for([RankedDisease(name="Không có trong graph", probability=0.5)]) == []


def test_edges_for_deduplicates_blank_and_repeated_candidate_names() -> None:
    db = _session()
    db.add(
        DiseaseSymptomEdge(
            disease_id="Cúm mùa",
            symptom="sốt",
            weight=0.8,
            is_discriminative=True,
        )
    )
    db.commit()

    graph = DiseaseSymptomGraph(db)
    edges = graph.edges_for(
        [
            RankedDisease(name=" Cúm mùa ", probability=0.6),
            RankedDisease(name="Cúm mùa", probability=0.4),
        ]
    )

    assert len(edges) == 1
    assert edges[0].disease_id == "Cúm mùa"
