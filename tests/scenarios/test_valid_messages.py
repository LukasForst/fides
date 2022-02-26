import json
from typing import List
from unittest import TestCase

from dacite import from_dict

from fides.messaging.model import NetworkMessage, PeerRecommendationResponse, PeerIntelligenceResponse
from fides.model.alert import Alert
from fides.model.peer import PeerInfo
from fides.model.recommendation import Recommendation
from fides.model.threat_intelligence import ThreatIntelligence
from tests.load_fides import get_fides
from tests.messaging.messages import serialize, nl2tl_intelligence_request, nl2tl_peers_list, \
    nl2tl_recommendation_request, nl2tl_recommendation_response, nl2tl_alert, nl2tl_intelligence_response


class TestValidMessages(TestCase):

    def test_nl2tl_peers_list(self):
        f, messages = self.__get_fides()
        new_peers = [PeerInfo(id='peer#1', organisations=[]), PeerInfo(id='peer#2', organisations=[])]
        f.queue.send_message(serialize(nl2tl_peers_list(new_peers)))

        self.assertEqual(1, len(messages))
        self.assertEquals('tl2nl_peers_reliability', messages[0].type)

        peer_ids = [d['peer_id'] for d in messages[0].data]
        self.assertListEqual(
            [p.id for p in new_peers],
            peer_ids
        )

    def test_nl2tl_recommendation_request(self):
        f, messages = self.__get_fides()
        request_id, subject, peer = '1234', 'peer#1', PeerInfo('peer#asking', [])
        f.queue.send_message(serialize(nl2tl_recommendation_request(request_id, subject, peer)))

        self.assertEqual(1, len(messages))
        self.assertEquals('tl2nl_recommendation_response', messages[0].type)

    def test_nl2tl_recommendation_response(self):
        f, messages = self.__get_fides()
        # create peer in DB because this peer is responding to our request,
        # so we definitely know it
        sender = PeerInfo('sender#1', [])
        f.trust.determine_and_store_initial_trust(sender, get_recommendations=False)
        subject = PeerInfo('subject#1', [])
        f.trust.determine_and_store_initial_trust(subject, get_recommendations=False)

        responses = [PeerRecommendationResponse(
            sender, subject.id, Recommendation(
                competence_belief=0,
                integrity_belief=0,
                service_history_size=0,
                recommendation=0,
                initial_reputation_provided_by_count=0
            ))
        ]
        f.queue.send_message(serialize(nl2tl_recommendation_response(responses)))

        # updates for sender#1 and subject#1
        self.assertEqual(2, len(messages))
        self.assertEquals(2, len([m for m in messages if m.type == 'tl2nl_peers_reliability']))

    def test_nl2tl_alert(self):
        f, messages = self.__get_fides()

        sender = PeerInfo('sender#1', [])
        alert = Alert(target='target.com', score=0.1, confidence=0.2)
        f.queue.send_message(serialize(nl2tl_alert(sender, alert)))

        # updates for sender#1 and subject#1
        self.assertEqual(1, len(messages))
        self.assertEquals('tl2nl_peers_reliability', messages[0].type)

    def test_nl2tl_intelligence_request(self):
        f, messages = self.__get_fides()

        f.queue.send_message(
            serialize(nl2tl_intelligence_request('123', 'example.com', PeerInfo(id='peer#1', organisations=[])))
        )

        self.assertEqual(2, len(messages))
        self.assertEquals(1, len([m for m in messages if m.type == 'tl2nl_intelligence_response']))
        self.assertEquals(1, len([m for m in messages if m.type == 'tl2nl_peers_reliability']))

    def test_nl2tl_intelligence_response(self):
        f, messages = self.__get_fides()
        # create peer in DB because this peer is responding to our request,
        # so we definitely know it
        sender = PeerInfo('sender#1', [])
        f.trust.determine_and_store_initial_trust(sender, get_recommendations=False)

        responses = [PeerIntelligenceResponse(
            sender=sender, target='target.com', intelligence=ThreatIntelligence(
                score=0.4,
                confidence=0.6
            ))
        ]
        f.queue.send_message(serialize(nl2tl_intelligence_response(responses)))

        # updates for sender#1 and subject#1
        self.assertEqual(1, len(messages))
        self.assertEquals('tl2nl_peers_reliability', messages[0].type)

    @staticmethod
    def __get_fides():
        f = get_fides()
        messages: List[NetworkMessage] = []

        def on_message(m: str):
            messages.append(from_dict(data_class=NetworkMessage, data=json.loads(m)))

        f.queue.on_send_called = on_message
        f.listen()
        return f, messages
