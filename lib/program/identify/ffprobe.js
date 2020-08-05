"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://ffmpeg.org/",
	gentooPackage  : "media-video/ffmpeg",
	gentooUseFlags : "X alsa amr bzip2 dav1d encode fontconfig gnutls gpl iconv jpeg2k lzma mp3 network opengl openssl opus postproc svg theora threads truetype v4l vaapi vdpau vorbis vpx webp x264 xvid zlib",
	informational  : true
};

exports.bin = () => "ffprobe";
exports.args = state => (["-show_streams", "-show_format", state.input.filePath]);
