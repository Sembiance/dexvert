import {Format} from "../../Format.js";

export class cmsOrgan extends Format
{
	name        = "Creative Music System Intelligent Organ File";
	website     = "https://vgmpf.com/Wiki/index.php?title=Creative_Music_System_(DOS)";
	ext         = [".org"];
	magic       = ["Creative Music System Intelligent Organ music"];
	unsupported = true;
	notes       = "No modern converter known. The linked website states that there is a converter to convert to CMS, but I couldn't locate it.";
}
