from fastapi import APIRouter, HTTPException
from models import Connection
from typing import List, Optional
from database import get_driver

router = APIRouter()

@router.get("/connections/{node_id}", response_model=List[Connection])
def get_connections(
    node_id: str,
    relationship_type: Optional[str] = None,
    limit: int = 100
):
    """
    Get intertextual connections for a node from your Neo4j database.
    Relationship types: CITES, COMMENTARY_ON, EXPLICIT, BELONGS_TO, MEMBER_OF, etc.
    """
    driver = get_driver()
    try:
        with driver.session() as session:
            # Query based on your actual Neo4j schema
            if relationship_type:
                query = f"""
                MATCH (n)-[r:{relationship_type}]-(m)
                WHERE n.`<id>` = $node_id OR id(n) = toInteger($node_id)
                RETURN 
                    coalesce(n.`<id>`, id(n)) AS source,
                    coalesce(m.`<id>`, id(m)) AS target,
                    type(r) as rel_type,
                    m.name AS target_name,
                    labels(m) AS target_labels
                LIMIT $limit
                """
            else:
                query = """
                MATCH (n)-[r]-(m)
                WHERE n.`<id>` = $node_id OR id(n) = toInteger($node_id)
                RETURN 
                    coalesce(n.`<id>`, id(n)) AS source,
                    coalesce(m.`<id>`, id(m)) AS target,
                    type(r) as rel_type,
                    m.name AS target_name,
                    labels(m) AS target_labels
                LIMIT $limit
                """
            
            records = session.run(query, {"node_id": node_id, "limit": limit})
            results = []
            for rec in records:
                results.append(Connection(
                    source=str(rec["source"]),
                    target=str(rec["target"]),
                    type=rec["rel_type"],
                    strength=0.8,  # Default strength
                    metadata={
                        "target_name": rec.get("target_name", ""),
                        "target_labels": rec.get("target_labels", [])
                    }
                ))
            
            if not results:
                raise HTTPException(status_code=404, detail=f"No connections found for node: {node_id}")
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/connections/graph/{node_id}")
def get_graph_data(node_id: str, depth: int = 2):
    """
    Get full graph data (nodes + edges) for visualization.
    Includes nodes up to specified depth from the source node.
    """
    driver = get_driver()
    try:
        with driver.session() as session:
            # Multi-hop query based on your actual Neo4j schema
            query = f"""
            MATCH path = (n)-[*1..{depth}]-(m)
            WHERE n.`<id>` = $node_id OR id(n) = toInteger($node_id)
            WITH nodes(path) as pathNodes, relationships(path) as pathRels
            UNWIND range(0, size(pathRels)-1) as i
            WITH pathNodes[i] as source, pathRels[i] as rel, pathNodes[i+1] as target
            RETURN DISTINCT 
                coalesce(source.`<id>`, id(source)) as source_id,
                coalesce(target.`<id>`, id(target)) as target_id,
                type(rel) as rel_type,
                source.name as source_name,
                target.name as target_name,
                labels(source) as source_labels,
                labels(target) as target_labels,
                source.era as source_era,
                target.era as target_era
            LIMIT 200
            """
            
            records = session.run(query, {"node_id": node_id})
            
            nodes = {}
            links = []
            
            for rec in records:
                # Add source node
                source_id = str(rec["source_id"])
                if source_id not in nodes:
                    nodes[source_id] = {
                        "id": source_id,
                        "title": rec.get("source_name", source_id),
                        "type": rec.get("source_labels", ["Unknown"])[0] if rec.get("source_labels") else "Unknown",
                        "metadata": {
                            "labels": rec.get("source_labels", []),
                            "era": rec.get("source_era")
                        }
                    }
                
                # Add target node
                target_id = str(rec["target_id"])
                if target_id not in nodes:
                    nodes[target_id] = {
                        "id": target_id,
                        "title": rec.get("target_name", target_id),
                        "type": rec.get("target_labels", ["Unknown"])[0] if rec.get("target_labels") else "Unknown",
                        "metadata": {
                            "labels": rec.get("target_labels", []),
                            "era": rec.get("target_era")
                        }
                    }
                
                # Add link
                links.append({
                    "source": source_id,
                    "target": target_id,
                    "type": rec["rel_type"],
                    "strength": 0.7
                })
            
            return {
                "nodes": list(nodes.values()),
                "links": links
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
