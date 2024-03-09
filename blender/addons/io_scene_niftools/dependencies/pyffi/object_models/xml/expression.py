"""Expression parser (for arr1, arr2, cond, and vercond xml attributes of
<add> tag)."""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****
# --------------------------------------------------------------------------

import re
import sys  # stderr (for debugging)


class Expression(object):
    """This class represents an expression.

    >>> class A(object):
    ...     x = False
    ...     y = True
    >>> a = A()
    >>> e = Expression('x || y')
    >>> e.eval(a)
    1
    >>> Expression('99 & 15').eval(a)
    3
    >>> bool(Expression('(99&15)&&y').eval(a))
    True
    >>> a.hello_world = False
    >>> def nameFilter(s):
    ...     return 'hello_' + s.lower()
    >>> bool(Expression('(99 &15) &&WoRlD', name_filter = nameFilter).eval(a))
    False
    >>> Expression('c && d').eval(a)
    Traceback (most recent call last):
        ...
    AttributeError: 'A' object has no attribute 'c'
    >>> bool(Expression('1 == 1').eval())
    True
    >>> bool(Expression('(1 == 1)').eval())
    True
    >>> bool(Expression('1 != 1').eval())
    False
    """

    operators = set(('==', '!=', '>=', '<=', '&&', '||', '&', '|', '-', '!',
                     '<', '>', '/', '*', '+', '%'))

    def __init__(self, expr_str, name_filter=None):
        try:
            left, self._op, right = self._partition(expr_str)
            self._left = self._parse(left, name_filter)
            self._right = self._parse(right, name_filter)
        except:
            print("error while parsing expression '%s'" % expr_str)
            raise

    def eval(self, data=None):
        """Evaluate the expression to an integer."""

        if isinstance(self._left, Expression):
            left = self._left.eval(data)
        elif isinstance(self._left, str):
            if self._left == '""':
                left = ""
            else:
                left = data
                for part in self._left.split("."):
                    left = getattr(left, part)
        elif isinstance(self._left, type):
            left = isinstance(data, self._left)
        elif self._left is None:
            pass
        else:
            assert (isinstance(self._left, int))  # debug
            left = self._left

        if not self._op:
            return left

        if isinstance(self._right, Expression):
            right = self._right.eval(data)
        elif isinstance(self._right, str):
            if (not self._right) or self._right == '""':
                right = ""
            else:
                right = getattr(data, self._right)
        elif isinstance(self._right, type):
            right = isinstance(data, self._right)
        elif self._right is None:
            pass
        else:
            assert (isinstance(self._right, int))  # debug
            right = self._right

        if self._op == '==':
            return left == right
        elif self._op == '!=':
            return left != right
        elif self._op == '>=':
            return left >= right
        elif self._op == '<=':
            return left <= right
        elif self._op == '&&':
            return left and right
        elif self._op == '||':
            return left or right
        elif self._op == '&':
            return left & right
        elif self._op == '|':
            return left | right
        elif self._op == '-':
            return left - right
        elif self._op == '!':
            return not (right)
        elif self._op == '>':
            return left > right
        elif self._op == '<':
            return left < right
        elif self._op == '/':
            return left / right
        elif self._op == '*':
            return left * right
        elif self._op == '+':
            return left + right
        elif self._op == '%':
            return left % right
        else:
            raise NotImplementedError("expression syntax error: operator '" + self._op + "' not implemented")

    def __str__(self):
        """Reconstruct the expression to a string."""

        left = str(self._left) if not self._left is None else ""
        if not self._op: return left
        right = str(self._right) if not self._right is None else ""
        return left + ' ' + self._op + ' ' + right

    @classmethod
    def _parse(cls, expr_str, name_filter=None):
        """Returns an Expression, string, or int, depending on the
        contents of <expr_str>."""
        if not expr_str:
            # empty string
            return None
        # brackets or operators => expression
        if ("(" in expr_str) or (")" in expr_str):
            return Expression(expr_str, name_filter)
        for op in cls.operators:
            if expr_str.find(op) != -1:
                return Expression(expr_str, name_filter)
        # try to convert it to an integer
        try:
            return int(expr_str)
        # failed, so return the string, passed through the name filter
        except ValueError:
            pass
        m = re.match(r'^([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)$', expr_str)
        if m:
            ver = (
                (int(m.group(1)) << 24)
                + (int(m.group(2)) << 16)
                + (int(m.group(3)) << 8)
                + int(m.group(4))
            )
            return ver
        # apply name filter on each component separately
        # (where a dot separates components)
        if name_filter is None:
            name_filter = lambda x: x
        return '.'.join(name_filter(comp)
                        for comp in expr_str.split("."))
        return expr_str

    @classmethod
    def _partition(cls, expr_str):
        """Partitions expr_str. See examples below.

        >>> Expression._partition('abc || efg')
        ('abc', '||', 'efg')
        >>> Expression._partition('(a== b) &&(( b!=c)||d )')
        ('a== b', '&&', '( b!=c)||d')
        >>> Expression._partition('!(1 <= 2)')
        ('', '!', '(1 <= 2)')
        >>> Expression._partition('')
        ('', '', '')
        """

        # strip whitespace
        expr_str = expr_str.strip()

        # all operators have a left hand side and a right hand side
        # except for negation, so let us deal with that case first
        if expr_str.startswith("!"):
            return "", "!", expr_str[1:].strip()

        # check if the left hand side starts with brackets
        # and if so, find the position of the starting bracket and the ending
        # bracket
        left_startpos, left_endpos = cls._scan_brackets(expr_str)
        if left_startpos == 0:
            # yes, it is a bracketted expression
            # so remove brackets and whitespace,
            # and let that be the left hand side
            left_str = expr_str[left_startpos + 1:left_endpos].strip()
            # if there is no next token, then just return the expression
            # without brackets
            if left_endpos + 1 == len(expr_str):
                return left_str, "", ""
            # the next token should be the operator
            # find the position where the operator should start
            op_startpos = left_endpos + 1
            while expr_str[op_startpos] == " ":
                op_startpos += 1
            # to avoid confusion between && and &, and || and |,
            # let's first scan for operators of two characters
            # and then for operators of one character
            for op_endpos in range(op_startpos + 1, op_startpos - 1, -1):
                op_str = expr_str[op_startpos:op_endpos + 1]
                if op_str in cls.operators:
                    break
            else:
                raise ValueError("expression syntax error: expected operator at '%s'" % expr_str[op_startpos:])
        else:
            # it's not... so we need to scan for the first operator
            for op_startpos, ch in enumerate(expr_str):
                if ch == ' ': continue
                if ch == '(' or ch == ')':
                    raise ValueError("expression syntax error: expected operator before '%s'" % expr_str[op_startpos:])
                # to avoid confusion between && and &, and || and |,
                # let's first scan for operators of two characters
                for op_endpos in range(op_startpos + 1, op_startpos - 1, -1):
                    op_str = expr_str[op_startpos:op_endpos + 1]
                    if op_str in cls.operators:
                        break
                else:
                    continue
                break
            else:
                # no operator found, so we are done
                left_str = expr_str.strip()
                op_str = ''
                right_str = ''
                return left_str, op_str, right_str
            # operator found! now get the left hand side
            left_str = expr_str[:op_startpos].strip()

        # now we have done the left hand side, and the operator
        # all that is left is to process the right hand side
        right_startpos, right_endpos = cls._scan_brackets(expr_str, op_endpos + 1)
        if right_startpos >= 0:
            # yes, we found a bracketted expression
            # so remove brackets and whitespace,
            # and let that be the right hand side
            right_str = expr_str[right_startpos + 1:right_endpos].strip()
            # check for trailing junk
            if expr_str[right_endpos + 1:] and not expr_str[right_endpos + 1:] == ' ':
                for op in cls.operators:
                    if expr_str.find(op) != -1:
                        break
                else:
                    raise ValueError(
                        "expression syntax error: unexpected trailing characters '%s'" % expr_str[right_endpos + 1:])
                # trailing characters contain an operator: do not remove
                # brackets but take
                # everything to be the right hand side (this happens for
                # instance in '(x <= y) && (y <= z) && (x != z)')
                right_str = expr_str[op_endpos + 1:].strip()
        else:
            # no, so just take the whole expression as right hand side
            right_str = expr_str[op_endpos + 1:].strip()
            # check that it is a valid expression
            if ("(" in right_str) or (")" in right_str):
                raise ValueError("expression syntax error: unexpected brackets in '%s'" % right_str)
        return left_str, op_str, right_str

    @staticmethod
    def _scan_brackets(expr_str, fromIndex=0):
        """Looks for matching brackets.

        >>> Expression._scan_brackets('abcde')
        (-1, -1)
        >>> Expression._scan_brackets('()')
        (0, 1)
        >>> Expression._scan_brackets('(abc(def))g')
        (0, 9)
        >>> s = '  (abc(dd efy 442))xxg'
        >>> start_pos, end_pos = Expression._scan_brackets(s)
        >>> print(s[start_pos+1:end_pos])
        abc(dd efy 442)
        """
        start_pos = -1
        end_pos = -1
        scan_depth = 0
        for scan_pos in range(fromIndex, len(expr_str)):
            scan_char = expr_str[scan_pos]
            if scan_char == "(":
                if start_pos == -1:
                    start_pos = scan_pos
                scan_depth += 1
            elif scan_char == ")":
                scan_depth -= 1
                if scan_depth == 0:
                    end_pos = scan_pos
                    break
        else:
            if start_pos != -1 or end_pos != -1:
                raise ValueError("expression syntax error (non-matching brackets?)")
        return start_pos, end_pos

    def map_(self, func):
        if isinstance(self._left, Expression):
            self._left.map_(func)
        else:
            self._left = func(self._left)
        if isinstance(self._right, Expression):
            self._right.map_(func)
        else:
            self._right = func(self._right)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
