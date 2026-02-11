def analysis_page():
    st.header("🎯 Component & Layer Analysis")
    st.caption("Detailed upgrade impact analysis for specific Pega / CDH components")

    # ── Selection ────────────────────────────────────────────────
    component = st.selectbox(
        "Which component / area do you want to analyze?",
        options=[
            "CDH Real-time Events / Stream Service",
            "Next-Best-Action / Strategy Framework",
            "Adaptive Models & Model Management",
            "Kafka Integration (embedded vs external)",
            "Hazelcast Clustering & Caching",
            "Search & Reporting Service (SRS)",
            "Database Schema Changes (PostgreSQL / Oracle)",
            "Pega Web Tier / Web Mashup / Portal",
            "Decision Data / Decision Strategies",
            "Custom Rulesets & Java Code",
            "Authentication / SSO / Security",
            "OpenShift / Kubernetes Deployment Artifacts",
            "Monitoring, Logging & Alerting",
            "Performance & Scalability Aspects"
        ],
        index=0
    )

    analysis_type = st.selectbox(
        "What kind of analysis do you need?",
        [
            "Upgrade Impact & Breaking Changes",
            "Deprecated / Replaced Features",
            "Migration Steps & Recommendations",
            "Risks & Severity Assessment",
            "Effort / Complexity Estimation",
            "Performance & Scalability Impact",
            "Configuration Changes Required",
            "Compatibility with Infinity 25.1"
        ]
    )

    # Optional context from user
    col1, col2 = st.columns([3, 2])
    with col1:
        current_setup = st.text_area(
            "Current implementation / configuration (optional but very helpful)",
            height=110,
            placeholder="Examples:\n• Using embedded Kafka for real-time events\n• Hazelcast embedded mode\n• Custom adaptive model predictors\n• Traditional 3-tier deployment",
            help="The more context you provide, the more accurate and tailored the analysis will be."
        )
    with col2:
        specific_questions = st.text_area(
            "Specific questions / concerns",
            height=110,
            placeholder="Examples:\n• Will our current decision strategies require rewrite?\n• How many days effort for Kafka migration?\n• What is the risk level?",
        )

    if st.button("🔍 Run Component Analysis", type="primary"):
        if not component:
            st.warning("Please select a component to analyze.")
            return

        payload = {
            "component": component,
            "analysis_type": analysis_type,
            "current_setup": current_setup.strip(),
            "specific_questions": specific_questions.strip()
        }

        with st.spinner(f"Analyzing **{component}** → {analysis_type} ..."):
            try:
                response = requests.post(
                    f"{API_URL}/analyze-component",
                    json=payload,
                    timeout=90
                )
                response.raise_for_status()
                result = response.json()

                # ── Result presentation ───────────────────────────────
                impact_level = result.get("impact_level", "medium").lower()

                if "critical" in impact_level or "high" in impact_level:
                    st.error(f"**High / Critical Impact Detected**")
                elif "medium" in impact_level:
                    st.warning(f"**Medium Impact**")
                else:
                    st.success(f"**Low Impact**")

                st.markdown("### Summary")
                st.markdown(result.get("summary", "No summary provided"))

                # Detailed explanation
                if "details" in result:
                    with st.expander("Detailed Explanation", expanded=True):
                        st.markdown(result["details"])

                # Recommendations
                if "recommendations" in result and result["recommendations"]:
                    st.subheader("Recommended Actions")
                    for i, rec in enumerate(result["recommendations"], 1):
                        st.markdown(f"{i}. {rec}")

                # Effort / timeline hint
                if "effort" in result:
                    st.metric("Estimated Effort", result["effort"])

                # Raw output for debugging
                with st.expander("Raw JSON Response (debug)"):
                    st.json(result)

            except requests.exceptions.RequestException as e:
                st.error(f"Backend error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")


def ingest_page():
    st.header("🕷️ Knowledge Base Ingestion")
    st.caption("Add Pega documentation, release notes, community posts, etc. to the vector database")

    # ── Current status ───────────────────────────────────────────
    try:
        health = requests.get(f"{API_URL}/health", timeout=6).json()
        if health.get("status") == "healthy":
            stats = health.get("vector_store", {})
            col1, col2, col3 = st.columns(3)
            col1.metric("Documents", stats.get("total_documents", 0))
            col2.metric("Embedding model", stats.get("embedding_model", "—"))
            col3.metric("Collection", stats.get("collection_name", "—"))
        else:
            st.warning("Backend is online but vector store not ready yet.")
    except:
        st.error("Cannot connect to backend API")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["📄 Manual URLs", "🚀 Guided Ingestion", "📁 Upload Files"])

    with tab1:
        st.subheader("Add specific Pega documentation URLs")

        urls_text = st.text_area(
            "Paste URLs (one per line)",
            height=140,
            placeholder="https://docs.pega.com/bundle/platform/page/platform/upgrade/deprecated-features.html\nhttps://docs.pega.com/bundle/decisioning/page/decisioning/cdh-upgrade.html\n..."
        )

        if st.button("Ingest Selected URLs", type="primary", disabled=not urls_text.strip()):
            urls = [line.strip() for line in urls_text.splitlines() if line.strip().startswith("http")]

            if not urls:
                st.warning("No valid URLs found.")
            else:
                with st.spinner(f"Ingesting {len(urls)} URLs..."):
                    try:
                        r = requests.post(
                            f"{API_URL}/ingest/urls",
                            json={"urls": urls, "source": "manual"},
                            timeout=180
                        )
                        r.raise_for_status()
                        result = r.json()
                        st.success(f"Ingestion started: {result.get('message', 'OK')}")
                        st.info(f"Job ID: {result.get('job_id', '—')}")
                    except Exception as e:
                        st.error(f"Ingestion request failed: {e}")

    with tab2:
        st.subheader("Guided / Full Pega 25.1 ingestion")

        st.markdown("Common useful ingestion presets:")

        presets = [
            {"name": "Upgrade Guide + Deprecated Features", "key": "upgrade"},
            {"name": "CDH / Decisioning changes 25.1", "key": "cdh"},
            {"name": "OpenShift / Kubernetes deployment", "key": "openshift"},
            {"name": "All critical deprecations & breaking changes", "key": "deprecations"},
        ]

        selected_preset = st.radio(
            "Select preset",
            options=[p["name"] for p in presets],
            index=0
        )

        preset_key = next(p["key"] for p in presets if p["name"] == selected_preset)

        if st.button(f"Start Ingestion: **{selected_preset}**", type="primary"):
            with st.spinner("Starting guided ingestion..."):
                try:
                    r = requests.post(
                        f"{API_URL}/ingest/preset",
                        json={"preset": preset_key},
                        timeout=60
                    )
                    r.raise_for_status()
                    result = r.json()
                    st.success(result.get("message", "Ingestion job started"))
                    if "job_id" in result:
                        st.info(f"Track job: {result['job_id']}")
                except Exception as e:
                    st.error(f"Failed to start preset ingestion: {e}")

    with tab3:
        st.subheader("Upload your own documents")
        st.info("PDF, HTML, Markdown, TXT supported (max 20 MB per file)")

        uploaded = st.file_uploader(
            "Select files",
            type=["pdf", "html", "htm", "md", "txt", "text"],
            accept_multiple_files=True,
            help="You can upload multiple files at once"
        )

        if uploaded and st.button("Upload & Index Files", type="primary"):
            with st.spinner("Uploading and indexing files..."):
                files = [("files", (f.name, f.getvalue(), "application/octet-stream")) for f in uploaded]

                try:
                    r = requests.post(
                        f"{API_URL}/ingest/files",
                        files=files,
                        timeout=300
                    )
                    r.raise_for_status()
                    result = r.json()
                    st.success(f"{len(uploaded)} file(s) processed successfully")
                    st.info(result.get("message", "Indexing complete"))
                except Exception as e:
                    st.error(f"File ingestion failed: {str(e)[:200]}")