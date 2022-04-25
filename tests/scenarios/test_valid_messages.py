from unittest import TestCase

from fides.messaging.model import PeerRecommendationResponse, PeerIntelligenceResponse
from fides.model.alert import Alert
from fides.model.peer import PeerInfo
from fides.model.recommendation import Recommendation
from fides.model.threat_intelligence import ThreatIntelligence, SlipsThreatIntelligence
from tests.load_fides import get_fides_stream
from tests.messaging.messages import serialize, nl2tl_intelligence_request, nl2tl_peers_list, \
    nl2tl_recommendation_request, nl2tl_recommendation_response, nl2tl_alert, nl2tl_intelligence_response


class TestValidMessages(TestCase):

    def test_nl2tl_peers_list(self):
        f, messages, _ = get_fides_stream()
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
        f, messages, _ = get_fides_stream()
        request_id, subject, peer = '1234', 'peer#1', PeerInfo('peer#asking', [])
        f.queue.send_message(serialize(nl2tl_recommendation_request(request_id, subject, peer)))

        self.assertEqual(1, len(messages))
        self.assertEquals('tl2nl_recommendation_response', messages[0].type)

    def test_nl2tl_recommendation_response(self):
        f, messages, _ = get_fides_stream()
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
        f, messages, _ = get_fides_stream()

        sender = PeerInfo('sender#1', [])
        alert = Alert(target='target.com', score=0.1, confidence=0.2)
        f.queue.send_message(serialize(nl2tl_alert(sender, alert)))

        # updates for sender#1 and subject#1
        self.assertEqual(1, len(messages))
        self.assertEquals('tl2nl_peers_reliability', messages[0].type)

    def test_nl2tl_intelligence_request(self):
        f, messages, _ = get_fides_stream()

        f.queue.send_message(
            serialize(nl2tl_intelligence_request('123', 'example.com', PeerInfo(id='peer#1', organisations=[])))
        )

        self.assertEqual(2, len(messages))
        self.assertEquals(1, len([m for m in messages if m.type == 'tl2nl_intelligence_response']))
        self.assertEquals(1, len([m for m in messages if m.type == 'tl2nl_peers_reliability']))

    def test_nl2tl_intelligence_response(self):
        f, messages, _ = get_fides_stream()
        # create peer in DB because this peer is responding to our request,
        # so we definitely know it
        sender1 = PeerInfo('sender#1', [])
        f.trust.determine_and_store_initial_trust(sender1, get_recommendations=False)
        sender2 = PeerInfo('sender#2', [], '1.2.3.4')
        f.trust.determine_and_store_initial_trust(sender2, get_recommendations=False)

        responses = [PeerIntelligenceResponse(
            sender=sender1, target='target.com', intelligence=ThreatIntelligence(
                score=0.4,
                confidence=0.6
            )),
            PeerIntelligenceResponse(
                sender=sender2, target='target.com', intelligence=ThreatIntelligence(
                    score=1,
                    confidence=1
                ))
        ]
        f.queue.send_message(serialize(nl2tl_intelligence_response(responses)))

        # updates for sender#1 and subject#1
        self.assertEqual(1, len(messages))
        self.assertEquals('tl2nl_peers_reliability', messages[0].type)

    def test_nl2tl_intelligence_response_with_valid_ip_data(self):
        f, messages, _ = get_fides_stream()
        sender1 = PeerInfo('sender#1', [])
        f.trust.determine_and_store_initial_trust(sender1, get_recommendations=False)

        # second sender has IP address, so we can utilise even Slips TI for the computation
        sender2 = PeerInfo('sender#2', [], '1.2.3.4')
        f.trust.determine_and_store_initial_trust(sender2, get_recommendations=False)
        f.ti_db.save(SlipsThreatIntelligence(score=1, confidence=1, target=sender2.ip))

        responses = [PeerIntelligenceResponse(
            sender=sender1, target='target.com', intelligence=ThreatIntelligence(
                score=0.4,
                confidence=0.4
            )),
            PeerIntelligenceResponse(
                sender=sender2, target='target.com', intelligence=ThreatIntelligence(
                    score=1,
                    confidence=1
                ))
        ]
        f.queue.send_message(serialize(nl2tl_intelligence_response(responses)))

        # updates for sender#1 and subject#1
        self.assertEqual(1, len(messages))
        self.assertEquals('tl2nl_peers_reliability', messages[0].type)
