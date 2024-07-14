import {Format} from "../../Format.js";

export class microsoftAgentCharacter extends Format
{
	name           = "Microsoft Agent Character";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Agent_character";
	ext            = [".acs", ".acf", ".aca"];
	forbidExtMatch = true;
	magic          = ["Microsoft Agent Character", /^fmt\/1893( |$)/];
	unsupported    = true;
	notes          = `
		Step 1 would just be extracting the embedded images and audio. Full file format details available in sandbox/txt/MSAgentDataSpecification_v1_4.htm
		Bonus points: Animate the character in a couple poses/animations and create animated GIFs`;
}
