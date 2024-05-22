import json
from json import JSONEncoder

import pandas as pd
import streamlit as st
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "pl", "model_name": "pl_core_news_sm"},
        {"lang_code": "en", "model_name": "en_core_web_lg"},
    ],
}

provider = NlpEngineProvider(nlp_configuration = configuration)
nlp_engine_with_polish = provider.create_engine()

@st.cache_resource()
def analyzer_engine():
    return AnalyzerEngine(nlp_engine=nlp_engine_with_polish, supported_languages=["pl", "en"])

@st.cache_resource()
def anonymizer_engine():
    return AnonymizerEngine()


def get_supported_entities():
    return analyzer_engine().get_supported_entities()

def get_supported_anonymizers():
    return anonymizer_engine().get_anonymizers()


def analyze(text, entities, analyzer_engine, score_threshold):
    if "All" in entities:
        entities = None
    return analyzer_engine.analyze(
        text=text,
        language="en",
        entities=entities,
        score_threshold=score_threshold,
        return_decision_process=True,
    )


def anonymize(text, analyze_results):
    res = anonymizer_engine().anonymize(text, analyze_results)
    return res.text


st.set_page_config(page_title="Presidio analyzer", layout="wide")

st_entities = st.sidebar.multiselect(
    label="Which entities to look for?",
    options=get_supported_entities(),
    default=list(get_supported_entities()),
)


st_threshold = st.sidebar.slider(
    label="Acceptance threshold", min_value=0.0, max_value=1.0, value=0.35
)


analyzer_load_state = st.info(f"Starting analyzer...")
engine = analyzer_engine()
analyzer_load_state.empty()



col1, col2 = st.columns(2)


col1.subheader("Input text:")
st_text = col1.text_area(
    label="Enter text",
    value="",
    height=400,
)


col2.subheader("Anonymized text:")
st_analyze_results = analyze(
    text=st_text,
    entities=st_entities,
    analyzer_engine=engine,
    score_threshold=st_threshold,
)
st_anonymize_results = anonymize(st_text, st_analyze_results)
col2.text_area(label="", value=st_anonymize_results, height=400, disabled=True)



st.subheader("Findings")
try:
    if st_analyze_results and all(k in st_analyze_results[0].to_dict() for k in ['entity_type', 'start', 'end', 'score']):
        df = pd.DataFrame.from_records([r.to_dict() for r in st_analyze_results])
        df = df[["entity_type", "start", "end", "score"]].rename(
            {
                "entity_type": "Entity type",
                "start": "Start",
                "end": "End",
                "score": "Confidence",
            },
            axis=1,
        )
    else:
        df = pd.DataFrame(columns=['Entity type', 'Start', 'End', 'Confidence'])
except Exception as e:
    st.error(f"Failed to process analysis results: {str(e)}")
    df = pd.DataFrame(columns=['Entity type', 'Start', 'End', 'Confidence'])


st.dataframe(df, width=1000)


class ToDictEncoder(JSONEncoder):
    def default(self, o):
        return o.to_dict()


if st.button("Analyze"):
    st.json(json.dumps(st_analyze_results, cls=ToDictEncoder))
