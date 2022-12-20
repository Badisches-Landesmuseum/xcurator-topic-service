from rabbitmq_proto_lib.listener import RabbitListener

from models.detection_status import DetectionStatus
from proto.dreipc.asset.topicmodeling import TopicDeletionActionProto, EnrichmentStatusProto
from proto.dreipc.q8r.proto.asset import DocumentProto, DeleteProjectAssets
from repositories.detection_result_repository import DetectionResultRepository


class DeletionRabbitListener(RabbitListener):

    def __init__(self, repository: DetectionResultRepository, project_id):

        self.name = 'asset.document.topic.deleted'
        self.exchange_name = 'assets'
        self.routing_keys = ['document.deleted', 'project.assets.deleted']
        self.dead_letter_exchange = "assets-dlx"
        self.prefetch_count = 1
        self.repository = repository
        self.project_id = project_id

    async def on_message(self, body, message):

        if body.project_id != self.project_id and self.project_id != '606ee5bf6769f83e24dc16cc':
            return

        if isinstance(body, DeleteProjectAssets):
            try:
                project_id = body.id
                self.repository.delete_project(project_id=project_id)
                status = DetectionStatus.DONE
            except:
                status = DetectionStatus.ERROR

        elif isinstance(body, DocumentProto):
            try:
                project_id = body.id
                self.repository.delete_entries_by_document(document_id=body.id,
                                                           project_id=body.project_id)
                status = DetectionStatus.DONE
            except:
                status = DetectionStatus.ERROR
        else:
            return

        proto_result = TopicDeletionActionProto(
            document_id=body.id,
            project_id=project_id,
            status=EnrichmentStatusProto.from_string(status),
            provided_by='topic-modeling-service')

        await self.convert_and_send(self.name, proto_result, self.exchange_name)
