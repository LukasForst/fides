import json
from dataclasses import asdict
from typing import List

from fides.messaging.model import NetworkMessage, PeerRecommendationResponse, PeerIntelligenceResponse
from fides.model.alert import Alert
from fides.model.aliases import Target, PeerId
from fides.model.peer import PeerInfo


def serialize(m: NetworkMessage) -> str:
    return json.dumps(asdict(m))


def nl2tl_peers_list(
        peers=None
) -> NetworkMessage:
    if peers is None:
        peers = [PeerInfo(id='peer#1', organisations=[]), PeerInfo(id='peer#2', organisations=[])]
    return NetworkMessage(
        version=1,
        type='nl2tl_peers_list',
        data={
            'peers': peers,
        }
    )


def nl2tl_recommendation_request(
        request_id: str,
        subject: PeerId,
        peer: PeerInfo
) -> NetworkMessage:
    return NetworkMessage(
        version=1,
        type='nl2tl_recommendation_request',
        data={
            'request_id': request_id,
            'sender': peer,
            'payload': subject
        }
    )


def nl2tl_recommendation_response(
        responses: List[PeerRecommendationResponse]
) -> NetworkMessage:
    return NetworkMessage(
        version=1,
        type='nl2tl_recommendation_response',
        data=[
            {'sender': r.sender, 'payload': {'subject': r.subject, 'recommendation': r.recommendation}}
            for r in responses
        ]
    )


def nl2tl_alert(
        sender: PeerInfo,
        alert: Alert
) -> NetworkMessage:
    return NetworkMessage(
        version=1,
        type='nl2tl_alert',
        data={
            'sender': sender,
            'payload': alert
        }
    )


def nl2tl_intelligence_request(
        request_id: str,
        target: Target,
        peer: PeerInfo
) -> NetworkMessage:
    return NetworkMessage(
        version=1,
        type='nl2tl_intelligence_request',
        data={
            'request_id': request_id,
            'sender': peer,
            'payload': target
        }
    )


def nl2tl_intelligence_response(
        responses: List[PeerIntelligenceResponse]
) -> NetworkMessage:
    return NetworkMessage(
        version=1,
        type='nl2tl_intelligence_response',
        data=[
            {'sender': r.sender, 'payload': {'target': r.target, 'intelligence': r.intelligence}}
            for r in responses
        ]
    )
