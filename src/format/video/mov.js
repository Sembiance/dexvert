import {xu} from "xu";
import {Format} from "../../Format.js";

const _MOV_MAGIC = [
	"Apple QuickTime movie", "QuickTime Movie", "Mac QuickTime video", "ISO Media, Apple QuickTime movie", "Apple QuickTime Film", "video/quicktime", /^MacBinary II.+'MooV'/, /Format: MP4 Video\[qt\s*]/,
	"Format: MP4 Video[qt", /^x-fmt\/384( |$)/];
const _MOV_EXT = [".mov", ".omv", ".pmv", ".qt"];
export {_MOV_MAGIC, _MOV_EXT};

export class mov extends Format
{
	name         = "Apple QuickTime movie";
	website      = "http://fileformats.archiveteam.org/wiki/QuickTime";
	ext          = _MOV_EXT;
	mimeType     = "video/quicktime";
	magic        = _MOV_MAGIC;
	idMeta       = ({macFileType}) => macFileType?.toLowerCase()==="moov" || macFileType==="MMov";	// I've encountered MooV and Moov, so just lowercase it
	trustMagic   = true;
	metaProvider = ["mplayer"];
	converters   = dexState => [
		"ffmpeg", "ffmpeg[libre]",
		(dexState.f.input.size<(xu.MB*25) ? "qt_flatt" : "qtflat"),
		...(dexState.f.input.size<(xu.MB*200) ? ["mencoderWinXP", "quickTimePlayer", "corelPhotoPaint[outType:avi]", "xanim"] : [])
	];
	notes = xu.trim`
		So quicktime movies require both a 'moov' section that contains movie metadata and info about the movie and a 'mdat' section that contains the actual movie contents.
		Early quicktime movies had the 'moov' section in the resource fork of the file and the 'mdat' section in the data fork.
		Sadly on my PC/Mac 'hybrid' CDs, the resource fork got stripped during mastering the PC side, so there is no 'moov' section on the PC files.
		Luckilly in these cases you can see they usually included an .avi alternative on the PC side, and of course the Mac side has the full quicktime movie, fully working.
		There are a handful of cases where the on a pure PC only CD there are 'dead' .mov files that are missing their 'moov' data, but there isn't anything really that can be done here.
		In theor it might be possible to train a generative AI model to examine tens of thousands of working quicktime .mov files, examining the 'mdat' section and seeing how it relates to the 'moov' section.
		Then maybe it would be possible to feed it some of these 'bare mdat' files and have it generate a 'moov' section that would work well enough to convert, but that's not something I'm capable of doing myself and it might not work anyways.
		Some more info about the issue: https://preservation.tylerthorsted.com/2023/10/06/quicktime-moov/
		Finally, ffmpeg itself can't deal with MacBinary 2 versions of quicktime movies (these include both the mdat data fork and moov resource fork data in 1 file), but the 'qtflat' tool can flatten these into a video file ffmpeg can work with`;
}
