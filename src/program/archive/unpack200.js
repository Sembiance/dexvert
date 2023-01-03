import {Program} from "../../Program.js";
import {path} from "std";

export class unpack200 extends Program
{
	website   = "https://adoptium.net";
	package   = "dev-java/openjdk-bin";
	bin       = "/opt/openjdk-bin-8/bin/unpack200";
	args      = async r => [r.inFile(), await r.outFile("out.jar")];
	renameOut = { name : (r, originalInput) => path.basename(originalInput.base, originalInput.base.toLowerCase().endsWith(".pack.gz") ? ".pack.gz" : originalInput.ext) };
}
