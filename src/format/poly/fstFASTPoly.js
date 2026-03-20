import {Format} from "../../Format.js";

export class fstFASTPoly extends Format
{
	name           = "fstFAST Poly";
	ext            = [".fst"];
	forbidExtMatch = true;
	magic          = [/^geArchive: FST_FAST( |$)/];
	converters     = ["poly2glb[type:fastFST]"];
}
