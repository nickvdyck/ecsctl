from ecsctl.models import Cluster
from typing import Any, Dict


def deserialize_cluster(cluster: Dict[str, Any]) -> Cluster:
    return Cluster(
        cluster["clusterArn"],
        cluster["clusterName"],
        cluster["status"],
        cluster["registeredContainerInstancesCount"],
        cluster["activeServicesCount"],
        cluster["runningTasksCount"],
        cluster["pendingTasksCount"],
        cluster.get("statistics", []),
        cluster["settings"],
        cluster["capacityProviders"],
        cluster.get("defaultCapacityProviderStrategy", []),
        cluster.get("tags", []),
    )


def serialize_cluster(cluster: Cluster) -> Dict[str, Any]:
    return {
        "arn": cluster.arn,
        "name": cluster.name,
        "status": cluster.status,
        "instances": cluster.status,
        "services": cluster.services,
        "running_tasks": cluster.running_tasks,
        "pending_tasks": cluster.pending_tasks,
        "statistics": cluster.statistics,
        "settings": cluster.settings,
        "capacity_providers": cluster.capacity_providers,
        "default_capacity_provider_strategy": cluster.default_capacity_provider_strategy,
        "tags": cluster.tags,
    }
