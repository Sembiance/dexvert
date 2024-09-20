import {Format} from "../../Format.js";

export class pack200 extends Format
{
	name       = "Pack200 Compressed JAR";
	ext        = [".pack", ".pack.gz"];
	website    = "https://docs.oracle.com/en/java/javase/13/docs/specs/pack-spec.html";
	magic      = ["JAR compressed with pack200", "application/x-java-pack200"];
	converters = ["unpack200"];
}
