import json
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(layout="wide")

# -----------------------------
# Load data
# -----------------------------
with open("data/grade7_knowledge_base.json", "r", encoding="utf-8") as f:
    data_g7 = json.load(f)

with open("data/grade8_knowledge_base.json", "r", encoding="utf-8") as f:
    data_g8 = json.load(f)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Select Grade")
grade = st.sidebar.radio("Grade", [7, 8])

data = data_g7 if grade == 7 else data_g8
concepts = data["concepts"]
activities = data.get("activities", [])

# -----------------------------
# Session state
# -----------------------------
if "selected_concept" not in st.session_state:
    st.session_state.selected_concept = None

# -----------------------------
# Domain colors
# -----------------------------
DOMAIN_COLORS = {
    "Physics (The Physical World)": "#2563EB",
    "Chemistry (The World of Matter)": "#16A34A",
    "Biology (The Living World)": "#EA580C",
    "Earth & Space Science": "#7C3AED",
    "Scientific Inquiry & Investigative Process": "#6B7280",
}

# -----------------------------
# Build graph
# -----------------------------
nodes = []
edges = []

def add_node(node):
    if node.id not in {n.id for n in nodes}:
        nodes.append(node)

# ---- Domains ----
domains = sorted(set(c["domain"] for c in concepts))
for domain in domains:
    add_node(Node(
        id=f"domain::{domain}",
        label=domain.replace(" (", "\n("),
        size=60,
        shape="box",
        color=DOMAIN_COLORS.get(domain, "#64748B"),
        font={"size": 18, "color": "white"}
    ))

# ---- Strands ----
strands = sorted(set(c["strand"] for c in concepts))
for strand in strands:
    add_node(Node(
        id=f"strand::{strand}",
        label=strand,
        size=35,
        shape="ellipse",
        color="#9CA3AF",
        font={"size": 14, "color": "black"}
    ))

# ---- Concepts ----
concept_names = set()
for c in concepts:
    concept_names.add(c["concept_name"])
    add_node(Node(
        id=f"concept::{c['concept_name']}",
        label=c["concept_name"],
        size=22,
        shape="dot",
        color=DOMAIN_COLORS.get(c["domain"], "#64748B"),
        borderWidth=3 if any(a.get("parent_concept") == c["concept_name"] for a in activities) else 1,
        borderColor="#111827"
    ))

# ---- Edges ----
for c in concepts:
    edges.append(Edge(
        source=f"domain::{c['domain']}",
        target=f"strand::{c['strand']}",
        color="#CBD5E1"
    ))
    edges.append(Edge(
        source=f"strand::{c['strand']}",
        target=f"concept::{c['concept_name']}",
        color="#CBD5E1"
    ))

    for linked in c.get("interconnections", []):
        if linked in concept_names:
            edges.append(Edge(
                source=f"concept::{c['concept_name']}",
                target=f"concept::{linked}",
                color="#FCA5A5"
            ))

# -----------------------------
# Graph config (CRITICAL)
# -----------------------------
config = Config(
    width=1200,
    height=700,
    directed=False,
    physics=True,
    hierarchical=False
)

# -----------------------------
# Render
# -----------------------------
st.title("📘 NCERT Knowledge Graph")

result = agraph(
    nodes=nodes,
    edges=edges,
    config=config
)

# -----------------------------
# Handle click (THIS FIXES IT)
# -----------------------------
if result and isinstance(result, dict):
    clicked_nodes = result.get("nodes", [])
    if clicked_nodes:
        node_id = clicked_nodes[0].get("id", "")
        if node_id.startswith("concept::"):
            st.session_state.selected_concept = node_id.replace("concept::", "")

# -----------------------------
# Sidebar details
# -----------------------------
st.sidebar.header("Concept Details")

if st.session_state.selected_concept:
    concept = next(c for c in concepts if c["concept_name"] == st.session_state.selected_concept)
    st.sidebar.subheader(concept["concept_name"])
    st.sidebar.write(concept.get("brief_explanation", ""))
    st.sidebar.markdown(f"**Chapter:** {', '.join(concept.get('chapter_references', []))}")
    st.sidebar.markdown(f"**Type:** {concept.get('concept_type', '-')}")
    st.sidebar.markdown(f"**Cognitive Level:** {concept.get('cognitive_level', '-')}")

    related_activities = [a for a in activities if a.get("parent_concept") == concept["concept_name"]]
    if related_activities:
        st.sidebar.markdown("### Activities")
        for a in related_activities:
            with st.sidebar.expander(a.get("activity_name", "Activity")):
                st.write(a.get("activity_type", ""))
                st.write(a.get("learning_goal", ""))
else:
    st.sidebar.info("Click a concept node to view details.")
