import {Format} from "../../Format.js";

export class greenstreetPublisher extends Format
{
	name           = "Greenstreet Publisher Document/Snippet";
	website        = "http://fileformats.archiveteam.org/wiki/Greenstreet_Publisher";
	ext            = [".dtp", ".srp"];
	forbidExtMatch = true;
	magic          = ["Greenstreet Publisher document", "Greenstreet Publisher snippet", /^fmt\/1415|1416( |$)/];
	notes          = "I could open these just fine under Win2k with Publishing Suite 99, but it can't save in ANY other format, and print to file crashes QEMU, sigh.";
	unsupported    = true;
}
