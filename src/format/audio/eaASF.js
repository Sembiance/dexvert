import {xu} from "xu";
import {Format} from "../../Format.js";

export class eaASF extends Format
{
	name             = "Electronic Arts ASF";
	website          = "http://fileformats.archiveteam.org/wiki/Electronic_Arts_AS4_/_ASF_Music";
	ext              = [".asf", ".as4"];
	forbidExtMatch   = true;
	confidenceAdjust = () => -10;	// Reduce by 10 so that video/eaTQI matches first
	magic            = ["Electronic Arts ASF video", "FIFA 2004 audio file", "'Need for Speed: Underground' soundtrack", "vgmstream: ea_schl", "vgmstream: ea_schl_fixed", "Electronic Arts Multimedia (ea)", /^x-fmt\/137( |$)/];
	weakMagic        = ["Electronic Arts Multimedia (ea)"];
	converters       = ["vgmstream[types:ea_schl,ea_schl_fixed]", "ffmpeg[outType:mp3][format:ea]"];
}
