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
            # Using n.id property (not deprecated id() function)
            if relationship_type:
                query = f"""
                MATCH (n)-[r:{relationship_type}]-(m)
                WHERE n.id = $node_id
                RETURN 
                    n.id AS source,
                    m.id AS target,
                    type(r) as rel_type,
                    coalesce(m.name, m.title, m.id) AS target_name,
                    labels(m) AS target_labels
                LIMIT $limit
                """
            else:
                query = """
                MATCH (n)-[r]-(m)
                WHERE n.id = $node_id
                RETURN 
                    n.id AS source,
                    m.id AS target,
                    type(r) as rel_type,
                    coalesce(m.name, m.title, m.id) AS target_name,
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
def get_graph_data(
    node_id: str, 
    depth: int = 2,
    relationship_type: Optional[str] = None,
    limit: int = 200
):
    """
    Get full graph data (nodes + edges) for visualization.
    Includes nodes up to specified depth from the source node.
    
    Args:
        node_id: Starting node ID
        depth: Number of hops (1-3)
        relationship_type: Optional filter by relationship type
        limit: Maximum number of results
    """
    driver = get_driver()
    
    # Validate depth
    if depth < 1 or depth > 3:
        raise HTTPException(status_code=400, detail="Depth must be between 1 and 3")
    
    try:
        with driver.session() as session:
            # Build relationship filter
            rel_filter = f":{relationship_type}" if relationship_type and relationship_type != "all" else ""
            
            # Multi-hop query based on your actual Neo4j schema
            # Using n.id property (not deprecated id() function)
            query = f"""
            MATCH path = (n)-[{rel_filter}*1..{depth}]-(m)
            WHERE n.id = $node_id
            WITH nodes(path) as pathNodes, relationships(path) as pathRels
            UNWIND range(0, size(pathRels)-1) as i
            WITH pathNodes[i] as source, pathRels[i] as rel, pathNodes[i+1] as target
            RETURN DISTINCT 
                source.id as source_id,
                target.id as target_id,
                type(rel) as rel_type,
                coalesce(source.name, source.title, source.id) as source_name,
                coalesce(target.name, target.title, target.id) as target_name,
                labels(source) as source_labels,
                labels(target) as target_labels,
                source.era as source_era,
                target.era as target_era,
                coalesce(source.content, source.snippet) as source_content,
                coalesce(target.content, target.snippet) as target_content
            LIMIT $limit
            """
            
            records = session.run(query, {"node_id": node_id, "limit": limit})
            
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
                        "snippet": (rec.get("source_content", "")[:100] + "...") if rec.get("source_content") else "",
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
                        "snippet": (rec.get("target_content", "")[:100] + "...") if rec.get("target_content") else "",
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
            
            if not nodes:
                raise HTTPException(status_code=404, detail=f"No graph data found for node: {node_id}")
            
            return {
                "nodes": list(nodes.values()),
                "links": links,
                "stats": {
                    "total_nodes": len(nodes),
                    "total_links": len(links),
                    "depth": depth,
                    "relationship_types": list(set(link["type"] for link in links))
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/connections/relationship-types")
def get_relationship_types():
    """
    Get all available relationship types in the graph database.
    Useful for filters and UI options.
    """
    driver = get_driver()
    try:
        with driver.session() as session:
            query = """
            CALL db.relationshipTypes() YIELD relationshipType
            RETURN relationshipType
            ORDER BY relationshipType
            LIMIT 50
            """
            records = session.run(query)
            types = [rec["relationshipType"] for rec in records]
            
            return {
                "relationship_types": types,
                "total": len(types)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/connections/stats")
def get_graph_stats():
    """
    Get overall statistics about the graph database.
    """
    driver = get_driver()
    try:
        with driver.session() as session:
            # Get node count
            node_query = "MATCH (n) RETURN count(n) as node_count"
            node_result = session.run(node_query)
            node_count = node_result.single()["node_count"]
            
            # Get relationship count
            rel_query = "MATCH ()-[r]->() RETURN count(r) as rel_count"
            rel_result = session.run(rel_query)
            rel_count = rel_result.single()["rel_count"]
            
            # Get node labels
            labels_query = "CALL db.labels() YIELD label RETURN label ORDER BY label"
            labels_result = session.run(labels_query)
            labels = [rec["label"] for rec in labels_result]
            
            # Get relationship types
            types_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"
            types_result = session.run(types_query)
            rel_types = [rec["relationshipType"] for rec in types_result]
            
            return {
                "nodes": {
                    "total": node_count,
                    "labels": labels,
                    "label_count": len(labels)
                },
                "relationships": {
                    "total": rel_count,
                    "types": rel_types,
                    "type_count": len(rel_types)
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
