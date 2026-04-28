import {Format} from "../../Format.js";

export class cmsOrgan extends Format
{
	name        = "Creative Music System Intelligent Organ File";
	ext         = [".org"];
	magic       = ["Creative Music System Intelligent Organ music"];
	unsupported = true;	// only 113 unique files on discmaster. Started a converter, but gave up (see vibe/legacy/cmsOrgan) trying to get DEMO.ORG to convert like the expected WAV from: https://www.youtube.com/watch?v=nAt1rWF-kqE
	notes       = "No modern converter known. The linked website states that there is a converter to convert to CMS, but I couldn't locate it.";
}
