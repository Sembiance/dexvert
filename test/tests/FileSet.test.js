import {assertStrictEquals} from "https://deno.land/std@0.111.0/testing/asserts.ts";
import {FileSet} from "../../src/FileSet.js";

Deno.test("create", async () =>
{
	const a = await FileSet.create([
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);
	const b = await FileSet.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", files : {primary : ["some.big.txt.file.txt", "subDir/txt.b", "subDir/symlinkFile", "subDir/more_sub/c.txt", "subDir/more_sub/third"]}});
	const c = b.clone();
	const d = b.clone();
	const e = await FileSet.create({primary : [
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]});
	d.changeRoot("/tmp/path/dir");

	[a, b, c, e].forEach(o =>
	{
		assertStrictEquals(o.root, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.files.primary.length, 5);
		assertStrictEquals(o.primaries.length, 5);
		assertStrictEquals(o.all.length, 5);
		assertStrictEquals(o.primary.name, "some.big.txt.file");
		assertStrictEquals(o.primary.size, 6);
		assertStrictEquals(o.primaries[2].isSymlink, true);
		assertStrictEquals(o.all[2].isSymlink, true);
		assertStrictEquals(o.files.primary[2].isSymlink, true);
	});
});

Deno.test("changeRoot", async () =>
{
	const a = await FileSet.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", files : {primary : ["some.big.txt.file.txt", "subDir/txt.b", "subDir/symlinkFile", "subDir/more_sub/c.txt", "subDir/more_sub/third"]}});
	const b = a.clone();
	b.changeRoot("/some/other/dir/");

	// test original
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.files.primary.length, 5);
	assertStrictEquals(a.primaries.length, 5);
	assertStrictEquals(a.all.length, 5);
	assertStrictEquals(a.primary.name, "some.big.txt.file");
	assertStrictEquals(a.primary.size, 6);
	assertStrictEquals(a.primaries[2].isSymlink, true);
	assertStrictEquals(a.all[2].isSymlink, true);
	assertStrictEquals(a.files.primary[2].isSymlink, true);
	assertStrictEquals(a.all[2].rel, "subDir/symlinkFile");

	// test clone
	assertStrictEquals(b.root, "/some/other/dir");
	assertStrictEquals(b.files.primary.length, 5);
	assertStrictEquals(b.primaries.length, 5);
	assertStrictEquals(b.all.length, 5);
	assertStrictEquals(b.primary.name, "some.big.txt.file");
	assertStrictEquals(b.primary.size, 6);
	assertStrictEquals(b.primaries[2].isSymlink, true);
	assertStrictEquals(b.all[2].isSymlink, true);
	assertStrictEquals(b.files.primary[2].isSymlink, true);
	assertStrictEquals(b.all[2].rel, "subDir/symlinkFile");
	assertStrictEquals(b.all[2].root, "/some/other/dir");
	assertStrictEquals(b.all[2].absolute, "/some/other/dir/subDir/symlinkFile");
	assertStrictEquals(b.all[2].dir, "/some/other/dir/subDir");
	assertStrictEquals(b.all[2].name, "symlinkFile");
});

Deno.test("addFile", async () =>
{
	const a = await FileSet.create([
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b"]);
	await a.addFile("/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile");
	await a.addFile("primary", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt");
	await a.addFile("primary", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third");
	const b = await FileSet.create([
		"/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt",
		"/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b"]);
	await b.addFiles("primary", ["/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/c.txt", "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third"]);

	[a, b].forEach(o =>
	{
		assertStrictEquals(o.root, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.files.primary.length, 5);
		assertStrictEquals(o.primaries.length, 5);
		assertStrictEquals(o.all.length, 5);
		assertStrictEquals(o.primary.name, "some.big.txt.file");
		assertStrictEquals(o.primary.size, 6);
		assertStrictEquals(o.primaries[2].isSymlink, true);
		assertStrictEquals(o.all[2].isSymlink, true);
		assertStrictEquals(o.files.primary[2].isSymlink, true);
	});
});
