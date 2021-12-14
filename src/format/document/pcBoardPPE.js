import {Format} from "../../Format.js";

export class pcBoardPPE extends Format
{
	name           = "PCBoard Programming Language Executable";
	website        = "https://en-academic.com/dic.nsf/enwiki/3064510";
	ext            = [".ppe"];
	forbidExtMatch = true;
	magic          = ["PCBoard Programming Language Executable"];
	converters     = ["pplx"];
}
