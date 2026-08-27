from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# Configuracoes para compilacao com MinGW no Windows 64-bit
define_macros = []
extra_compile_args = []

if os.name == 'nt':
    # Define MS_WIN64 para corrigir erro de SIZEOF_VOID_P no GCC 64-bit
    define_macros.append(('MS_WIN64', None))
    # Otimizacao basica
    extra_compile_args.append("-O2")

extensions = [
    Extension("alterar_voz_core", ["alterar_voz_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("sync_assets_core", ["sync_assets_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("search_visuals_core", ["search_visuals_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("gerar_roteiro_core", ["gerar_roteiro_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("upload_tiktok_core", ["upload_tiktok_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("upload_youtube_core", ["upload_youtube_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("gerar_imagens_web_core", ["gerar_imagens_web_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("gerar_anime_core", ["gerar_anime_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("gerar_imagens_core", ["gerar_imagens_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("transcrever_audio_core", ["transcrever_audio_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("isolar_voz_core", ["isolar_voz_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("auto_playlist_core", ["auto_playlist_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("detect_faces_core", ["detect_faces_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("gerar_karaoke_core", ["gerar_karaoke_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("gerar_parallax_core", ["gerar_parallax_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("process_watermark_core", ["process_watermark_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("gerar_prompts_audio_core", ["gerar_prompts_audio_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("gerar_metadata_core", ["gerar_metadata_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("gerar_tags_core", ["gerar_tags_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("upscale_imagem_core", ["upscale_imagem_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("traduzir_tags_core", ["traduzir_tags_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("upload_master_lote_core", ["upload_master_lote_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("diretor_windows_cpu_core", ["diretor_windows_cpu_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("diretor_windows_core", ["diretor_windows_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("montador_windows_cpu_core", ["montador_windows_cpu_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("cameraman_cpu_core", ["cameraman_cpu_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
    Extension("narrador_cpu_core", ["narrador_cpu_core.pyx"], define_macros=define_macros, extra_compile_args=extra_compile_args),
]

setup(
    # language_level=3 garante compatibilidade com Python 3
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
)