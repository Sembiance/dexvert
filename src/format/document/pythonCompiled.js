import {Format} from "../../Format.js";

export class pythonCompiled extends Format
{
	name           = "Python Compiled Bytecode";
	website        = "http://fileformats.archiveteam.org/wiki/Python";
	ext            = [".pyc", ".pyo"];
	magic          = ["Python optimized code", /CPython \d\.. bytecode$/, /python \d\.. byte-compiled/, /^fmt\/(1109|1110)( |$)/];
	converters     = ["pycdc"];
}
