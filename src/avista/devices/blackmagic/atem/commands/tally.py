from construct import BitStruct, Struct, Flag, Int16ub, Padding, Rebuild, len_, this

from avista.devices.blackmagic.atem.constants import VideoSource
from .base import BaseCommand, EnumAdapter, clone_state_with_key, recalculate_synthetic_tally


class TallyBySource(BaseCommand):
    name = b'TlSr'
    format = Struct(
        'count' / Rebuild(Int16ub, len_(this.sources)),
        'sources' / Struct(
            'source' / EnumAdapter(VideoSource)(Int16ub),
            'tally' / BitStruct(
                'program' / Flag,
                'preview' / Flag,
                Padding(6)
            )
        )[this.count]
    )

    def apply_to_state(self, state):
        new_state, tally = clone_state_with_key(state, 'tally')

        tally['by_source'] = {
            source: {
                'program': tally.program,
                'preview': tally.preview
            }
            for source, tally in map(lambda s: (s.source, s.tally), self.sources)
        }

        return recalculate_synthetic_tally(new_state)
