import {Format} from "../../Format.js";

export class pythonCompiled extends Format
{
	name           = "Python Compiled Bytecode";
	website        = "http://fileformats.archiveteam.org/wiki/Python";
	ext            = [".pyc", ".pyo"];
	magic          = ["Python optimized code", "Format: Python Compiled Module", "Kompilierter Phyton Source Code", /CPython \d\.. bytecode$/, /python [\d.-]+ byte-compiled/, /^fmt\/(939|1106|1107|1108|1109|1110|1111|1112)( |$)/];
	converters     = ["pycdc"];
}
