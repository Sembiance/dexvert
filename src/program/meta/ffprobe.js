import {Program} from "../../Program.js";

export class ffprobe extends Program
{
	website = "https://ffmpeg.org/";
	gentooPackage = "media-video/ffmpeg";
	gentooUseFlags = "X alsa amr bzip2 dav1d encode fontconfig gnutls gpl iconv jpeg2k lzma mp3 network opengl openssl opus postproc svg theora threads truetype v4l vaapi vdpau vorbis vpx webp x264 xvid zlib";
	bin = "ffprobe";
	args = r => ["-show_streams", "-show_format", r.inFile()];
	post = r =>
	{
		let seenFormatSection = false;
		r.stdout.trim().split("\n").forEach(line =>
		{
			if(line.trim().startsWith("format_long_name="))
				r.meta.formatLongName = line.trim().substring("format_long_name=".length);

			if(line.trim()==="[FORMAT]")
			{
				seenFormatSection = true;
				return;
			}

			if(!seenFormatSection)
				return;
			
			const tag = (line.trim().match(/^TAG:(?<key>[^=]+)=(?<value>.+)$/) || {groups : {}}).groups;
			if(tag.key && tag.value && tag.key.trim().length>0 && tag.value.trim().length>0)
				r.meta[tag.key.trim()] = tag.value.trim();
		});
	}
}
