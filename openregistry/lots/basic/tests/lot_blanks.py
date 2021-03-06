# -*- coding: utf-8 -*-
from copy import deepcopy
from uuid import uuid4

from openregistry.api.utils import get_now
from openregistry.api.constants import ROUTE_PREFIX

from openregistry.lots.basic.models import Lot


# LotTest

def simple_add_lot(self):
    u = Lot(self.initial_data)
    u.lotID = "UA-X"
    u.assets = [uuid4().hex]

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.lotID == fromdb['lotID']
    assert u.doc_type == "Lot"

    u.delete_instance(self.db)


def check_lot_assets(self):


    def create_single_lot():
        response = self.app.post_json('/', {"data": self.initial_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        return response.json['data']


    # lot with a single assets
    self.initial_data["assets"] = [uuid4().hex]
    lot = create_single_lot()
    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(lot))
    self.assertEqual(response.json['data'], lot)

    # lot with different assets
    self.initial_data["assets"] = [uuid4().hex, uuid4().hex]
    lot = create_single_lot()
    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(set(response.json['data']), set(lot))
    self.assertEqual(response.json['data'], lot)

    # # lot with no assets
    self.initial_data["assets"] = []
    response = self.app.post_json('/', {"data": self.initial_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Please provide at least 1 item."], u'location': u'body', u'name': u'assets'}
    ])
    # # lot with equal assets
    id_ex = uuid4().hex
    self.initial_data["assets"] = [id_ex, id_ex]
    response = self.app.post_json('/', {"data": self.initial_data}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': [u"Assets should be unique"], u'location': u'body', u'name': u'assets'}
    ])


def change_draft_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    # Create lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Create new lot in 'draft' status
    draft_lot = deepcopy(draft_lot)
    draft_lot['assets'] = [uuid4().hex]
    response = self.app.post_json('/', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    # Move from 'draft' to 'pending' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'pending'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')

    # Move from 'pending' to 'draft'
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'draft'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    self.app.authorization = ('Basic', ('concierge', ''))

    # Create lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/', {'data': draft_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move last 'draft' lot to 'deleted' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'deleted'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'draft' to 'waiting' status
    # XXX TODO Waiting to Waiting
    # response = self.app.patch_json(
    #     '/{}?acc_token={}'.format(lot['id'], token),
    #     {'data': {'status': 'waiting'}},
    #     status=403,
    # )
    # self.assertEqual(response.status, '403 Forbidden')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertEqual(response.json['status'], 'error')


def change_waiting_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)


    self.app.authorization = ('Basic', ('concierge', ''))

    # Create new lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['assets'] = [uuid4().hex]
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/', {'data': draft_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


    self.app.authorization = ('Basic', ('broker', ''))

    # Create new lot in 'draft' status
    response = self.app.post_json('/', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'waiting' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'pending'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Create new lot in 'draft' status
    response = self.app.post_json('/', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'pending'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'pending' to 'verification' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'verification'}}
    )
    self.assertEqual(response.status, '200 OK')


    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'verification' to 'active.salable' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.salable'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'active.salable' to 'verification' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'verification'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'active.pending' to 'sold' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'sold'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


    self.app.authorization = ('Basic', ('broker', ''))

    lot = self.create_resource()

    # Move from 'waiting' to 'active.pending' status
    response = self.app.patch_json(
        '/{}'.format(lot['id']),
        {'data': {'status': 'active.pending'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'waiting' to 'sold' status
    response = self.app.patch_json(
        '/{}'.format(lot['id']),
        {'data': {'status': 'sold'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


def change_dissolved_lot(self):
    response = self.app.get('/')
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(len(response.json['data']), 0)

    self.app.authorization = ('Basic', ('broker', ''))

    # Create new lot in 'draft' status
    draft_lot = deepcopy(self.initial_data)
    draft_lot['assets'] = [uuid4().hex]
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'pending'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'pending' to 'verification' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'verification'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'waiting' to 'active.pending' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.salable'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


    self.app.authorization = ('Basic', ('concierge', ''))
    # Move from 'waiting' to 'active.pending' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.salable'}}
    )
    self.assertEqual(response.status, '200 OK')


    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'active.salable' to 'dissolved' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'dissolved'}}
    )
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data']['status'], 'dissolved')

    # Move from 'dissolved' to 'active.salable' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.salable'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'dissolved' to 'invalid' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'invalid'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'dissolved' to 'deleted' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'deleted'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'dissolved' to 'sold' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'sold'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')


    # Create new lot in 'draft' status for bot
    draft_lot = deepcopy(self.initial_data)
    draft_lot['assets'] = [uuid4().hex]
    draft_lot['status'] = 'draft'
    response = self.app.post_json('/', {'data': draft_lot})
    self.assertEqual(response.status, '201 Created')
    lot = response.json['data']
    token = response.json['access']['token']
    self.assertEqual(lot.get('status', ''), 'draft')

    response = self.app.get('/{}'.format(lot['id']))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['data'], lot)

    # Move from 'draft' to 'pending' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'pending'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'pending' to 'verification' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'verification'}}
    )
    self.assertEqual(response.status, '200 OK')


    self.app.authorization = ('Basic', ('concierge', ''))

    # Create lot in 'active.salable' status
    pending_lot = deepcopy(self.initial_data)
    pending_lot['status'] = 'active.salable'
    response = self.app.post_json('/', {'data': pending_lot}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'verification' to 'active.salable' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'active.salable'}}
    )
    self.assertEqual(response.status, '200 OK')

    # Move from 'active.pending' to 'dissolved' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'dissolved'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    self.app.authorization = ('Basic', ('broker', ''))

    # Move from 'active.pending' to 'dissolved' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'dissolved'}}
    )
    self.assertEqual(response.status, '200 OK')

    self.app.authorization = ('Basic', ('concierge', ''))

    # Move from 'dissolved' to 'deleted' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'deleted'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')

    # Move from 'dissolved' to 'sold' status
    response = self.app.patch_json(
        '/{}?acc_token={}'.format(lot['id'], token),
        {'data': {'status': 'sold'}},
        status=403,
    )
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
