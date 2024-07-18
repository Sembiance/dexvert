import {xu} from "xu";
import {Format} from "../../Format.js";

export class eaASF extends Format
{
	name             = "Electronic Arts ASF";
	website          = "http://fileformats.archiveteam.org/wiki/Electronic_Arts_AS4_/_ASF_Music";
	ext              = [".asf", ".as4"];
	forbidExtMatch   = true;
	confidenceAdjust = () => -10;	// Reduce by 10 so that video/eaTQI matches first
	magic            = ["Electronic Arts ASF video", "'Need for Speed: Underground' soundtrack", /^x-fmt\/137( |$)/];
	converters       = ["vgmstream"];
	verify           = ({meta}) => meta.duration>=(xu.SECOND*2);
}
