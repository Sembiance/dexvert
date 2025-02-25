import {Format} from "../../Format.js";

export class pocketWordDocument extends Format
{
	name           = "Pocket Word/Inkwriter/Notetaker document";
	ext            = [".pwd", ".pwi", ".psw"];
	forbidExtMatch = true;
	idCheck        = (inputFile, detections, {extMatch}) => extMatch || (/\.\d+$/i).test(inputFile.ext);
	magic          = ["Pocket Word document", "application/x-pocket-word", /^x-fmt\/(94|95)( |$)/];
	unsupported    = true;
}
