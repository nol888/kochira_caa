"""
:thinking_face: intensification.

!thinkball
"""

import random

from kochira.service import Service

service = Service(__name__, __doc__)

THINKING_FACES = [
    'thinking_face',
    'dhingin_face',
    'thinking_kara',
    'thinking_maou',
    'thinking_maou',
    'thinking_mawaru',
    'thinking_mawaru_ccw',
    'thinking_aoba',
    'thinking_mawaru_3d',
    'thinking_mawaru_3d_ccw',
    'thinking_mawaru_3d_backward',
    'thinking_mawaru_3d_forward',
    'thinkingpotato',
    'thinkpad',
    'thinking_v',
    'thinking_hanabatake',
    'thinking_chalk',
    'thinking_hazuki',
]

@service.command("!thinkball")
@service.command(".*:thinking_face:.*")
def thinkball(ctx):
    """
    Thinkball.

    Like an 8ball, but for thinking faces.
    """
    ctx.message(":{emoji}:".format(
        emoji=random.choice(THINKING_FACES)
    ))
