import {xu} from "xu";
import {Format} from "../../Format.js";

export class ibmStoryboardPic extends Format
{
	name           = "IBM Storyboard PIC";
	website        = "http://fileformats.archiveteam.org/wiki/Storyboard_PIC/CAP";
	ext            = [".pic", ".cap"];
	forbiddenExt   = [".txm"];
	forbidExtMatch = true;
	magic          = ["IBM Storyboard bitmap", "IBM Storyboard screen Capture"];
	notes          = xu.trim`
		Unable to use SBLIVE/PICTYPE.EXE to determine if it's valid due to that program not working with shell redirection (see sandbox/legacy/programs_and_formats/storyboardLivePicType.js)
		Several encountered .PIC files that PICTYPE does say are valid don't show in SHOWPIC.EXE for whatever reason.`;
	
	converters = ["imageAlchemy", "storyboardLiveShowPic"];
}
