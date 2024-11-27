import graphene
import pandas as pd

# Load dataset globally (update path as necessary)
try:
    df = pd.read_csv("sample_integration_data.csv")  # Ensure this file exists in your working directory
    print("Dataset loaded successfully!")
except FileNotFoundError:
    print("Error: 'sample_integration_data.csv' not found. Please place the file in the working directory.")
    df = pd.DataFrame()  # Empty DataFrame as fallback

class Node(graphene.ObjectType):
    name = graphene.String()

class Edge(graphene.ObjectType):
    consumer = graphene.String()
    producer = graphene.String()
    integration_type = graphene.String()
    context = graphene.String()

class Query(graphene.ObjectType):
    nodes = graphene.List(Node)
    edges = graphene.List(
        Edge,
        consumer=graphene.String(),
        producer=graphene.String(),
        integrationType=graphene.String(),
        context=graphene.String(),
        contextContains=graphene.String(),
        integrationTypeIn=graphene.List(graphene.String),
        first=graphene.Int(),
        last=graphene.Int()
    )

    def resolve_nodes(parent, info):
        global df
        if df.empty:
            return []

        # Extract unique nodes
        all_nodes = set(df['Consumer']).union(df['Producer'])
        return [{"name": node} for node in all_nodes]

    def resolve_edges(
        parent, info, consumer=None, producer=None,
        integrationType=None, context=None,
        contextContains=None, integrationTypeIn=None,
        first=None, last=None
    ):
        global df
        if df.empty:
            return []

        # Start with the full dataset
        filtered_edges = df.copy()

        # Apply filters
        if consumer:
            filtered_edges = filtered_edges[filtered_edges['Consumer'] == consumer]
        if producer:
            filtered_edges = filtered_edges[filtered_edges['Producer'] == producer]
        if integrationType:
            filtered_edges = filtered_edges[filtered_edges['Integration Type'] == integrationType]
        if context:
            filtered_edges = filtered_edges[filtered_edges['Context-Domain'] == context]
        if contextContains:
            filtered_edges = filtered_edges[
                filtered_edges['Context-Domain'].str.contains(contextContains, case=False, na=False)
            ]
        if integrationTypeIn:
            filtered_edges = filtered_edges[filtered_edges['Integration Type'].isin(integrationTypeIn)]

        # Convert rows to dictionaries
        results = [
            {
                "consumer": row['Consumer'],
                "producer": row['Producer'],
                "integration_type": row['Integration Type'],
                "context": row['Context-Domain']
            }
            for _, row in filtered_edges.iterrows()
        ]

        # Pagination
        if first:
            results = results[:first]
        if last:
            results = results[-last:]

        return results

# Create the schema
schema = graphene.Schema(query=Query)

# Confirm schema creation and inspect schema
try:
    print("Schema created successfully!")
    print("Query type fields:", list(schema.query._meta.fields.keys()))
except AttributeError as e:
    print("Error accessing schema attributes:", e)

# Debug the entire schema structure
print("\nDebugging schema:")
print(schema)
