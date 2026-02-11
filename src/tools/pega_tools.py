class PegaTools:
    def get_version_info(self):
        return {
            "source": "8.7.1",
            "target": "25.1",
            "environment": "openshift"
        }
    
    def get_cdh_components(self):
        return [
            "real-time-events",
            "next-best-action",
            "adaptive-models",
            "decisioning"
        ]
    
    def get_deprecated_features_87_to_25(self):
        return [
            {"feature": "Stream Service (embedded)", "replacement": "External Kafka"},
            {"feature": "Hazelcast embedded", "replacement": "Hazelcast client-server"},
            {"feature": "SRS (optional)", "replacement": "SRS (required)"}
        ]
