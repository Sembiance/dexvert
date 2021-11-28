import {Format} from "../../Format.js";

export class flf extends Format
{
	name       = "Turbo Rascal Syntax Error";
	website    = "https://lemonspawn.com/turbo-rascal-syntax-error-expected-but-begin/";
	ext        = [".flf"];
	magic      = ["Turbo Rascal Syntax Error"];
	converters = ["recoil2png"];
}
