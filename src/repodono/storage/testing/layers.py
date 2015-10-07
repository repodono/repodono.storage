# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import repodono.storage


class RepodonoStorageLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=repodono.storage)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'repodono.storage:default')


REPODONO_STORAGE_FIXTURE = RepodonoStorageLayer()


REPODONO_STORAGE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(REPODONO_STORAGE_FIXTURE,),
    name='RepodonoStorageLayer:IntegrationTesting'
)


REPODONO_STORAGE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(REPODONO_STORAGE_FIXTURE,),
    name='RepodonoStorageLayer:FunctionalTesting'
)


REPODONO_STORAGE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        REPODONO_STORAGE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='RepodonoStorageLayer:AcceptanceTesting'
)
