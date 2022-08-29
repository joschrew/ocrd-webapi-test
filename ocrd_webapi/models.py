from __future__ import annotations
from pydantic import BaseModel, Field, constr
from typing import Any, Dict, Optional, Union
from beanie import (
    Document,
    Link,
)
from uuid import UUID, uuid4
from ocrd_webapi import utils


class DiscoveryResponse(BaseModel):
    ram: Union[int, None] = Field(None, description='All available RAM in bytes')
    cpu_cores: Union[int, None] = Field(None, description='Number of available CPU cores')
    has_cuda: Union[bool, None] = Field(
        None, description="Whether deployment supports NVIDIA's CUDA"
    )
    cuda_version: Union[str, None] = Field(None, description='Major/minor version of CUDA')
    has_ocrd_all: Union[bool, None] = Field(
        None, description='Whether deployment is based on ocrd_all'
    )
    ocrd_all_version: Union[str, None] = Field(
        None, description='Git tag of the ocrd_all version implemented'
    )
    has_docker: Union[bool, None] = Field(
        None, description='Whether the OCR-D executables run in a Docker container'
    )


class Resource(BaseModel):
    id: str = Field(..., alias='@id', description='URL of this thing')
    description: Union[str, None] = Field(None, description='Description of the thing')

    class Config:
        allow_population_by_field_name = True


class WorkspaceRsrc(Resource):
    @staticmethod
    def from_id(uid) -> WorkspaceRsrc:
        return WorkspaceRsrc(id=utils.to_workspace_url(uid), description="Workspace")


class WorkflowRsrc(Resource):
    @staticmethod
    def from_id(uid) -> WorkflowRsrc:
        return WorkflowRsrc(id=utils.to_workflow_url(uid), description="Workflow")


class ProcessorArgs(BaseModel):
    workspace: Optional[WorkspaceRsrc] = None
    input_file_grps: Optional[str] = None
    output_file_grps: Optional[str] = None
    page_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}


class JobState(BaseModel):
    __root__: constr(regex=r'^(QUEUED|RUNNING|STOPPED)')


class Job(Resource):
    state: Optional[JobState] = None

    class Config:
        allow_population_by_field_name = True


class Processor(BaseModel):
    __root__: Any = Field(..., description='The ocrd-tool.json for a specific tool')


class ProcessorJob(Job):
    processor: Optional[Processor] = None
    workspace: Optional[WorkspaceRsrc] = None


class WorkflowArgs(BaseModel):
    workspace_id: str = None
    workflow_parameters: Optional[Dict[str, Any]] = {}


class WorkflowJobRsrc(Job):
    workflow: Optional[WorkflowRsrc]
    workspace: Optional[WorkspaceRsrc]

    @staticmethod
    def create(uid, workflow=WorkflowRsrc, workspace=WorkspaceRsrc, state: JobState = None) -> WorkflowJobRsrc:
        workflow_id = utils.get_workflow_id(workflow)
        job_url = utils.to_workflow_job_url(workflow_id, uid)
        return WorkflowJobRsrc(id=job_url, workflow=workflow, workspace=workspace, state=state,
                               description="Workflow-Job")


class WorkspaceDb(Document):
    """
    Model to store a workspace in the mongo-database.

    Information to handle workspaces and from bag-info.txt are stored here.

    Attributes:
        ocrd_identifier             Ocrd-Identifier (mandatory)
        bagit_profile_identifier    BagIt-Profile-Identifier (mandatory)
        ocrd_base_version_checksum  Ocrd-Base-Version-Checksum (mandatory)
        ocrd_mets                   Ocrd-Mets (optional)
        bag_info_adds               bag-info.txt can also (optionally) contain aditional
                                    key-value-pairs which are saved here
    """
    # TODO: no id is currently generated anywhere, but this might not work if the latter is changed
    id: str = Field(default_factory=uuid4)
    ocrd_identifier: str
    bagit_profile_identifier: str
    ocrd_base_version_checksum: Optional[str]
    ocrd_mets: Optional[str]
    bag_info_adds: Optional[dict]
    deleted: bool = False

    class Settings:
        name = "workspace"


class WorkflowJobDb(Document):
    """
    Model to store a Workflow-Job in the mongo-database.

    Attributes:
        id            the job's id
        workspace_id  id of the workspace on which this job is running
        workflow_id   id of the workflow the job is executing
        state         current state of the job
    """
    id: str = Field(default_factory=uuid4)
    workspace_id: str
    workflow_id: str
    state: str

    class Settings:
        name = "workflow_job"

    def to_rsrc(self) -> WorkflowJobDb:
        return WorkflowJobRsrc(id=utils.to_workflow_job_url(self.workflow_id, self.id),
                               workflow=WorkflowRsrc.from_id(self.workflow_id),
                               workspace=WorkspaceRsrc.from_id(self.workspace_id),
                               state=self.state, description="Workflow-Job")
