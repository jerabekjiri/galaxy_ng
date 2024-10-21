import logging
import json
import pytest
import os

from galaxy_ng.tests.integration.conftest import is_hub_4_7_or_higher
from galaxy_ng.tests.integration.utils.iqe_utils import sign_collection_on_demand, is_ocp_env, aap_gateway
from galaxy_ng.tests.integration.utils.repo_management_utils import create_repo_and_dist, \
    upload_new_artifact
# from galaxy_ng.tests.integration.utils.tools import generate_random_string
from galaxykit.collections import deprecate_collection, \
    move_or_copy_collection
from galaxykit.containers import create_container, delete_container
# from galaxykit.namespaces import add_group
from galaxykit.registries import create_registry, delete_registry
from galaxykit.remotes import create_remote, update_remote
from galaxykit.roles import put_update_role
from galaxykit.users import update_user
from galaxykit.utils import GalaxyClientError, wait_for_task
from galaxykit.client import BasicAuthClient


logger = logging.getLogger(__name__)


class TestLoadData:

    """
    Test loading data that will be verified at a later stage
    after the AAP upgrade or backup/restore
    """

    # @pytest.mark.min_hub_version("4.6dev")
    # @pytest.mark.load_data
    # def test_load_data(self, galaxy_client, data, ansible_config):
    #     """
    #     Test loading data that will be verified at a later stage
    #     after the AAP upgrade or backup/restore
    #     """
    #     gc = galaxy_client("admin")

    #     for group in data["groups"]:
    #         # creates a group, nothing happens if it already exists
    #         logger.debug(f"Creating group {group['name']}")
    #         gc.create_group(group["name"])

    #     for user in data["users"]:
    #         # creates a user, nothing happens if it already exists
    #         logger.debug(f"Creating user {user['username']}")
    #         _user = gc.get_or_create_user(user["username"], user["password"], group=None)
    #         update_body = {
    #             "id": _user[1]["id"],
    #             "username": user["username"],
    #             "email": user["email"],
    #             "password": user["password"],
    #             "is_superuser": user["is_superuser"],
    #         }
    #         # if it exists, we should update it
    #         update_user(gc, update_body)
    #         if user["group"]:
    #             group = gc.get_group(user["group"])
    #             gc.add_user_to_group(user["username"], group["id"])

    #     for ns in data["namespaces"]:
    #         logger.debug(f"Creating namespace {ns['name']}")
    #         gc.create_namespace(ns["name"], ns["group"],
    #                             object_roles=["galaxy.collection_namespace_owner"])
    #         add_group(gc, ns["name"], ns["group"],
    #                   object_roles=["galaxy.collection_namespace_owner"])

    #     if is_hub_4_7_or_higher(ansible_config):
    #         for repo in data["repositories"]:
    #             try:
    #                 logger.debug(f"Creating repository and distribution {repo['name']}")
    #                 create_repo_and_dist(gc, repo["name"])
    #             except GalaxyClientError as e:
    #                 if "This field must be unique" in e.response.text:
    #                     logger.debug(
    #                         f"Repository {repo['name']} already exists. Not a problem.")
    #                 else:
    #                     raise e

    #     for remote in data["remotes"]:
    #         try:
    #             logger.debug(f"Creating remote {remote['name']}")
    #             create_remote(gc, remote["name"], remote["url"], remote["signed_only"],
    #                           remote["tls_validation"])
    #         except GalaxyClientError as e:
    #             if "This field must be unique" in e.response.text:
    #                 logger.debug(f"Remote {remote['name']} already exists. Updating it.")
    #                 # let's update it, maybe the yaml file wants to change the details
    #                 update_remote(gc, remote["name"], remote["url"],
    #                               {"signed_only": remote["signed_only"],
    #                                "tls_validation": remote["tls_validation"]})
    #             else:
    #                 raise e

    #     for collection in data["collections"]:
    #         if (collection["repository"] != "published"
    #                 and not is_hub_4_7_or_higher(ansible_config)):
    #             continue

    #         try:
    #             artifact = upload_new_artifact(
    #                 gc, collection["namespace"], collection["repository"],
    #                 collection["version"], collection["name"])
    #             move_or_copy_collection(gc, artifact.namespace, artifact.name,
    #                                     artifact.version, "staging",
    #                                     destination=collection["repository"])
    #             if collection["signed"] and not is_ocp_env():
    #                 logger.debug("Signing collection")
    #                 sign_collection_on_demand(
    #                     gc, "ansible-default", collection["repository"],
    #                     artifact.namespace, artifact.name, artifact.version)
    #             if collection["signed"] and is_ocp_env():
    #                 # FIXME
    #                 logger.debug("Not Signing collection, collection signing not enabled"
    #                              "on ocp environment")
    #             if collection["deprecated"]:
    #                 logger.debug("Deprecating collection")
    #                 deprecate_collection(gc, collection["namespace"], artifact.name,
    #                                      repository=collection["repository"])
    #         except GalaxyClientError as e:
    #             if "already exists" in e.response.text:
    #                 logger.debug(f"Collection collection_dep_a_{collection['name']} "
    #                              f"already exists. Not doing anything")
    #             else:
    #                 raise e

    #     for role in data["roles"]:
    #         name = role["name"]
    #         description = role["description"]
    #         permissions = role["permissions"]
    #         try:
    #             logger.debug(f"Creating role {role['name']}")
    #             gc.create_role(name, description, permissions)
    #         except GalaxyClientError as e:
    #             if "This field must be unique" in e.response.text:
    #                 logger.debug(f"Role {role['name']} already exists. Updating it")
    #                 updated_body = {
    #                     "name": role["name"],
    #                     "description": description,
    #                     "permissions": permissions,
    #                 }
    #                 put_update_role(gc, name, updated_body)
    #             else:
    #                 raise e

    #     for remote_registry in data["remote_registries"]:
    #         try:
    #             logger.debug(f"Creating remote registry {remote_registry['name']}")
    #             create_registry(gc, remote_registry["name"], remote_registry["url"])
    #         except GalaxyClientError as e:
    #             if "This field must be unique" in e.response.text:
    #                 logger.debug(f"Remote registry {remote_registry['name']} already exists. "
    #                              f"Updating it")
    #                 delete_registry(gc, remote_registry['name'])
    #                 create_registry(gc, remote_registry["name"], remote_registry["url"])
    #             else:
    #                 raise e

    #     for ee in data["execution_environments"]:
    #         try:
    #             logger.debug(f"Creating execution environment {ee['name']}")
    #             create_container(gc, ee["name"], ee["upstream_name"], ee["remote_registry"])
    #         except GalaxyClientError as e:
    #             if "This field must be unique" in e.response.text:
    #                 logger.debug(f"Execution environment {ee['name']} already exists. "
    #                              f"Updating it")
    #                 delete_resp = delete_container(gc, ee["name"])
    #                 resp = json.loads(delete_resp.content.decode('utf-8'))
    #                 wait_for_task(gc, resp)
    #                 create_container(gc, ee["name"], ee["upstream_name"],
    #                                  ee["remote_registry"])
    #             else:
    #                 raise e


    @pytest.mark.min_hub_version("4.6dev")
    @pytest.mark.load_data
    def test_load_users_and_groups(self, galaxy_client, settings, data):

        if settings.get('ALLOW_LOCAL_RESOURCE_MANAGEMENT') is False:
            pytest.skip("this test relies on local resource creation")

        gc = galaxy_client("admin")

        for group in data["groups"]:
            # creates a group, nothing happens if it already exists
            logger.debug(f"Creating group {group['name']}")
            gc.create_group(group["name"])

        for user in data["users"]:
            # creates a user, nothing happens if it already exists
            logger.debug(f"Creating user {user['username']}")
            _user = gc.get_or_create_user(user["username"], user["password"], group=None)
            update_body = {
                "id": _user[1]["id"],
                "username": user["username"],
                "email": user["email"],
                "password": user["password"],
                "is_superuser": user["is_superuser"],
            }
            # if it exists, we should update it
            update_user(gc, update_body)
            if user["group"]:
                group = gc.get_group(user["group"])
                gc.add_user_to_group(user["username"], group["id"])


    @pytest.mark.skipif(not aap_gateway(), reason="Load data test was skipped. Only works with gateway enabled.")
    @pytest.mark.min_hub_version("4.6")
    @pytest.mark.load_data
    def test_load_gw_users_and_teams(self, galaxy_client, data):
        gc = galaxy_client("admin")
        username = os.environ.get('AAP_GATEWAY_ADMIN_USERNAME')
        password = os.environ.get('AAP_GATEWAY_ADMIN_PASSWORD')
        gw_client = BasicAuthClient(gc.galaxy_root, username, password)

        # org_name = f'hub_org_{generate_random_string()}'
        # org_data = gw_client.post(
        #     '/api/gateway/v1/organizations/',
        #     body=json.dumps({'name': org_name})
        # )
        created_teams = {}

        for team in data["teams"]:
            logger.debug(f"Creating team {team['name']}")
            # gw_client.post(
            #     '/api/gateway/v1/teams/',
            #     body=json.dumps({
            #         'name': team['name'],
            #         'organization': org_data['id']
            #     })
            # )
            created_team = gw_client.post(
                '/api/galaxy/_ui/v2/teams/',
                body=json.dumps({
                    'name': team['name']
                })
            )
            print(created_team, team, flush=True)
            logger.info(f'created_team: {created_team}')
            logger.debug(f'created_team: {created_team}')

            logger.info(f'team: {team}')
            logger.debug(f'team: {team}')
            print(created_team, team)

            created_teams.update({ team['name']: created_team['id'] })

        for user in data["users"]:
            logger.debug(f"Creating user {user['username']}")
            created_user = gw_client.post(
                '/api/gateway/v1/users/',
                body=json.dumps({
                    'username': user['username'],
                    'password': user['password'],
                    'group': None
                })
            )
            print('created user', created_user)
            # if it exists, we should update it
            updated_user = gw_client.patch(
                f'/api/gateway/v1/users/{created_user["id"]}/',
                body=json.dumps({
                    "id": created_user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "password": user["password"],
                    "is_superuser": user["is_superuser"],
                })
            )
            print('updated user', updated_user)

        # associate users to their teams
        for user in data["users"]:
            team_id = created_teams.get(user['team'])
            associate_user = gw_client.post(
                f'/api/gateway/v1/teams/{team_id}/users/associate/',
                body=json.dumps({
                    "instances": [user['id']]
                })
            )
            print('associate user', associate_user)

            # if user["group"]:
            #     group = gc.get_group(user["group"])
            #     gc.add_user_to_group(user["username"], group["id"])


    @pytest.mark.min_hub_version("4.6")
    @pytest.mark.load_data
    def test_load_namespaces(self, galaxy_client, data):
        gc = galaxy_client("admin")

        for ns in data["namespaces"]:
            logger.debug(f"Creating namespace {ns['name']}")
            gc.create_namespace(ns["name"], None, None)
            # gc.create_namespace(ns["name"], ns["group"],
            #                     object_roles=["galaxy.collection_namespace_owner"])
            # add_group(gc, ns["name"], ns["group"],
            #             object_roles=["galaxy.collection_namespace_owner"])


    @pytest.mark.min_hub_version("4.6")
    @pytest.mark.load_data
    def test_load_repositories_and_remotes(self, galaxy_client, data):
        gc = galaxy_client("admin")

        for repo in data["repositories"]:
            try:
                logger.debug(f"Creating repository and distribution {repo['name']}")
                create_repo_and_dist(gc, repo["name"])
            except GalaxyClientError as e:
                if "This field must be unique" in e.response.text:
                    logger.debug(
                        f"Repository {repo['name']} already exists. Not a problem.")
                else:
                    raise e

        for remote in data["remotes"]:
            try:
                logger.debug(f"Creating remote {remote['name']}")
                create_remote(gc, remote["name"], remote["url"], remote["signed_only"],
                              remote["tls_validation"])
            except GalaxyClientError as e:
                if "This field must be unique" in e.response.text:
                    logger.debug(f"Remote {remote['name']} already exists. Updating it.")
                    # let's update it, maybe the yaml file wants to change the details
                    update_remote(gc, remote["name"], remote["url"],
                                  {"signed_only": remote["signed_only"],
                                   "tls_validation": remote["tls_validation"]})
                else:
                    raise e


    @pytest.mark.min_hub_version("4.6")
    @pytest.mark.load_data
    def test_load_collections(self, galaxy_client, data, ansible_config):
        gc = galaxy_client("admin")

        for collection in data["collections"]:
            if (collection["repository"] != "published"
                    and not is_hub_4_7_or_higher(ansible_config)):
                continue

            try:
                artifact = upload_new_artifact(
                    gc, collection["namespace"], collection["repository"],
                    collection["version"], collection["name"])
                move_or_copy_collection(gc, artifact.namespace, artifact.name,
                                        artifact.version, "staging",
                                        destination=collection["repository"])
                if collection["signed"] and not is_ocp_env():
                    logger.debug("Signing collection")
                    sign_collection_on_demand(
                        gc, "ansible-default", collection["repository"],
                        artifact.namespace, artifact.name, artifact.version)
                if collection["signed"] and is_ocp_env():
                    # FIXME
                    logger.debug("Not Signing collection, collection signing not enabled"
                                 "on ocp environment")
                if collection["deprecated"]:
                    logger.debug("Deprecating collection")
                    deprecate_collection(gc, collection["namespace"], artifact.name,
                                         repository=collection["repository"])
            except GalaxyClientError as e:
                if "already exists" in e.response.text:
                    logger.debug(f"Collection collection_dep_a_{collection['name']} "
                                 f"already exists. Not doing anything")
                else:
                    raise e


    @pytest.mark.min_hub_version("4.6")
    @pytest.mark.load_data
    def test_load_roles(self, galaxy_client, data):
        gc = galaxy_client("admin")

        for role in data["roles"]:
            name = role["name"]
            description = role["description"]
            permissions = role["permissions"]
            try:
                logger.debug(f"Creating role {role['name']}")
                gc.create_role(name, description, permissions)
            except GalaxyClientError as e:
                if "This field must be unique" in e.response.text:
                    logger.debug(f"Role {role['name']} already exists. Updating it")
                    updated_body = {
                        "name": role["name"],
                        "description": description,
                        "permissions": permissions,
                    }
                    put_update_role(gc, name, updated_body)
                else:
                    raise e


    @pytest.mark.min_hub_version("4.6")
    @pytest.mark.load_data
    def test_load_remote_registries(self, galaxy_client, data):
        gc = galaxy_client("admin")

        for remote_registry in data["remote_registries"]:
            try:
                logger.debug(f"Creating remote registry {remote_registry['name']}")
                create_registry(gc, remote_registry["name"], remote_registry["url"])
            except GalaxyClientError as e:
                if "This field must be unique" in e.response.text:
                    logger.debug(f"Remote registry {remote_registry['name']} already exists. "
                                 f"Updating it")
                    delete_registry(gc, remote_registry['name'])
                    create_registry(gc, remote_registry["name"], remote_registry["url"])
                else:
                    raise e


    @pytest.mark.min_hub_version("4.6")
    @pytest.mark.load_data
    def test_load_execution_environments(self, galaxy_client, data):
        gc = galaxy_client("admin")

        for ee in data["execution_environments"]:
            try:
                logger.debug(f"Creating execution environment {ee['name']}")
                create_container(gc, ee["name"], ee["upstream_name"], ee["remote_registry"])
            except GalaxyClientError as e:
                if "This field must be unique" in e.response.text:
                    logger.debug(f"Execution environment {ee['name']} already exists. "
                                 f"Updating it")
                    delete_resp = delete_container(gc, ee["name"])
                    resp = json.loads(delete_resp.content.decode('utf-8'))
                    wait_for_task(gc, resp)
                    create_container(gc, ee["name"], ee["upstream_name"],
                                     ee["remote_registry"])
                else:
                    raise e
