import os
import scipy.io.wavfile
import torch
from pydub import AudioSegment, effects


def save_tensor_to_wav(audio_tensor: torch.Tensor, sample_rate: int, output_path: str):
    if torch.is_tensor(audio_tensor):
        audio_data = audio_tensor.detach().cpu().numpy()
    else:
        audio_data = audio_tensor

    scipy.io.wavfile.write(output_path, sample_rate, audio_data)


def post_process_audio(chunk_paths: list[str], output_path: str):
    combined = AudioSegment.empty()

    for path in chunk_paths:
        if not os.path.exists(path):
            continue
        segment = AudioSegment.from_file(path)
        combined += segment
        os.remove(path)

    combined = effects.normalize(combined)

    combined = combined.high_pass_filter(80)

    combined = combined.compress_dynamic_range()

    combined.export(output_path, format="mp3", bitrate="320k", parameters=["-q:a", "0"])
    return output_path
