import {Format} from "../../Format.js";

export class rag extends Format
{
	name       = "RAG-D";
	website    = "http://fileformats.archiveteam.org/wiki/RAG-D";
	ext        = [".rag"];
	magic      = ["RAG-D bitmap"];
	converters = ["recoil2png"];
}
