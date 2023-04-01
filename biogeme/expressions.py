""" Defines the various arithmetic expressions accepted by Biogeme.

:author: Michel Bierlaire

:date: Tue Mar 26 16:47:49 2019

"""

# Too constraining
# pylint: disable=invalid-name

# Too constraining
# pylint: disable=invalid-name, too-many-locals, too-many-arguments
# pylint: disable=too-many-instance-attributes, too-many-lines

import numpy as np
import biogeme.exceptions as excep
import biogeme.messaging as msg
import biogeme.cexpressions as ee


def isNumeric(obj):
    """Identifies if an object is numeric, that is int, float or bool.

    :param obj: any object
    :type obj: object

    :return: True if the object is int, float or bool.
    :rtype: bool
    """
    return isinstance(obj, (int, float, bool))


class Expression:
    """This is the general arithmetic expression in biogeme.
    It serves as a base class for concrete expressions.
    """

    def __init__(self):
        """Constructor"""

        self.logger = msg.bioMessage()
        """Logger that controls the output of
        messages to the screen and log file.
        Type: class :class:`biogeme.messaging.bioMessage`.
        """

        self.parent = None  #: Parent expression

        self.children = []

        self.elementaryExpressionIndex = None
        """Indices of the elementary expressions (dict)"""

        self.allFreeBetas = {}

        self.freeBetaNames = []

        self.allFixedBetas = {}

        self.fixedBetaNames = []

        self.allRandomVariables = None  #: dict of random variables

        self.variableNames = None  #: list of variables names

        self.randomVariableNames = None  #: list of random variables names

        self.allDraws = None  #: dict of draws

        self.drawNames = None  #: list of draw types

        self.numberOfDraws = None
        """number of draws for Monte Carlo integration
        """

        self._row = None
        """Row of the database where the values of the variables are found
        """

        self.betaIds = None
        """List of ids of the free beta parameters (those to be estimated)
        """

        self.freeBetaValues = None
        """List of values of the free beta parameters (those to be estimated)
        """

        self.fixedBetaValues = None
        """ List of values of the fixed beta parameters (those to be estimated)
        """

        self.expression_prepared = False
        """ If True, the expression is prepared to be used.
        """

        self.cpp = ee.pyEvaluateOneExpression()
        """ Interface to the C++ implementation
        """

        self.missingData = 99999
        """ Value interpreted as missing data
        """

    def __repr__(self):
        """built-in function used to compute the 'official' string reputation
        of an object

        :return: description of the expression
        :rtype: string

        """
        return self.__str__()

    def __add__(self, other):
        """
        Operator overloading. Generate an expression for addition.

        :param other: expression to be added
        :type other: biogeme.expressions.Expression

        :return: self + other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during addition to {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Plus(self, other)

    def __radd__(self, other):
        """
        Operator overloading. Generate an expression for addition.

        :param other: expression to be added
        :type other: biogeme.expressions.Expression

        :return: other + self
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.

        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during addition to {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Plus(other, self)

    def __sub__(self, other):
        """
        Operator overloading. Generate an expression for substraction.

        :param other: expression to substract
        :type other: biogeme.expressions.Expression

        :return: self - other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.

        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during substraction to {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Minus(self, other)

    def __rsub__(self, other):
        """
        Operator overloading. Generate an expression for substraction.

        :param other: expression to be substracted
        :type other: biogeme.expressions.Expression

        :return: other - self
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.

        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during substraction of {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Minus(other, self)

    def __mul__(self, other):
        """
        Operator overloading. Generate an expression for multiplication.

        :param other: expression to be multiplied
        :type other: biogeme.expressions.Expression

        :return: self * other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.

        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during multiplication '
                f'to {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Times(self, other)

    def __rmul__(self, other):
        """
        Operator overloading. Generate an expression for multiplication.

        :param other: expression to be multiplied
        :type other: biogeme.expressions.Expression

        :return: other * self
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during multiplication '
                f'to {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Times(other, self)

    def __div__(self, other):
        """
        Operator overloading. Generate an expression for division.

        :param other: expression for division
        :type other: biogeme.expressions.Expression

        :return: self / other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.

        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during division of {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Divide(self, other)

    def __rdiv__(self, other):
        """
        Operator overloading. Generate an expression for division.

        :param other: expression for division
        :type other: biogeme.expressions.Expression

        :return: other / self
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during division by {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Divide(other, self)

    def __truediv__(self, other):
        """
        Operator overloading. Generate an expression for division.

        :param other: expression for division
        :type other: biogeme.expressions.Expression

        :return: self / other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during division of {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Divide(self, other)

    def __rtruediv__(self, other):
        """
        Operator overloading. Generate an expression for division.

        :param other: expression for division
        :type other: biogeme.expressions.Expression

        :return: other / self
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            error_msg = (
                f'Invalid expression during division by {self}: [{other}]'
            )
            raise excep.biogemeError(error_msg)
        return Divide(other, self)

    def __neg__(self):
        """
        Operator overloading. Generate an expression for unary minus.

        :return: -self
        :rtype: biogeme.expressions.Expression
        """
        return UnaryMinus(self)

    def __pow__(self, other):
        """
        Operator overloading. Generate an expression for power.

        :param other: expression for power
        :type other: biogeme.expressions.Expression

        :return: self ^ other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.

        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return Power(self, other)

    def __rpow__(self, other):
        """
        Operator overloading. Generate an expression for power.

        :param other: expression for power
        :type other: biogeme.expressions.Expression

        :return: other ^ self
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return Power(other, self)

    def __and__(self, other):
        """
        Operator overloading. Generate an expression for logical and.

        :param other: expression for logical and
        :type other: biogeme.expressions.Expression

        :return: self and other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return And(self, other)

    def __rand__(self, other):
        """
        Operator overloading. Generate an expression for logical and.

        :param other: expression for logical and
        :type other: biogeme.expressions.Expression

        :return: other and self
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return And(other, self)

    def __or__(self, other):
        """
        Operator overloading. Generate an expression for logical or.

        :param other: expression for logical or
        :type other: biogeme.expressions.Expression

        :return: self or other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return Or(self, other)

    def __ror__(self, other):
        """
        Operator overloading. Generate an expression for logical or.

        :param other: expression for logical or
        :type other: biogeme.expressions.Expression

        :return: other or self
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return Or(other, self)

    def __eq__(self, other):
        """
        Operator overloading. Generate an expression for comparison.

        :param other: expression for equality
        :type other: biogeme.expressions.Expression

        :return: self == other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return Equal(self, other)

    def __ne__(self, other):
        """
        Operator overloading. Generate an expression for comparison.

        :param other: expression for difference
        :type other: biogeme.expressions.Expression

        :return: self != other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return NotEqual(self, other)

    def __le__(self, other):
        """
        Operator overloading. Generate an expression for comparison.

        :param other: expression for less or equal
        :type other: biogeme.expressions.Expression

        :return: self <= other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return LessOrEqual(self, other)

    def __ge__(self, other):
        """
        Operator overloading. Generate an expression for comparison.

        :param other: expression for greater or equal
        :type other: biogeme.expressions.Expression

        :return: self >= other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return GreaterOrEqual(self, other)

    def __lt__(self, other):
        """
        Operator overloading. Generate an expression for comparison.

        :param other: expression for less than
        :type other: biogeme.expressions.Expression

        :return: self < other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return Less(self, other)

    def __gt__(self, other):
        """
        Operator overloading. Generate an expression for comparison.

        :param other: expression for greater than
        :type other: biogeme.expressions.Expression

        :return: self > other
        :rtype: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        if not (isNumeric(other) or isinstance(other, Expression)):
            raise excep.biogemeError(
                f'This is not a valid expression: {other}'
            )
        return Greater(self, other)

    def _prepareFormulaForEvaluation(self, database):
        """Extract from the formula the elementary expressions (parameters,
        variables, random parameters) and decide a numbering convention.

        :raise biogemeError: if no database is given and the
            expressions involves variables.

        :raise biogemeError: if the expression involves MonteCarlo integration,
           and no database is provided.

        """

        if self.expression_prepared:
            return

        if database is not None:
            self.variableNames = list(database.data.columns.values)
        elif variables := self.setOfVariables():
            raise excep.biogemeError(
                f'No database is provided and the expression '
                f'contains variables: {variables}'
            )
        else:
            self.variableNames = []

        (
            self.elementaryExpressionIndex,
            self.allFreeBetas,
            self.freeBetaNames,
            self.allFixedBetas,
            self.fixedBetaNames,
            self.allRandomVariables,
            self.randomVariableNames,
            self.allDraws,
            self.drawNames,
        ) = defineNumberingOfElementaryExpressions([self], self.variableNames)

        # List of ids of the free beta parameters (those to be estimated)
        self.betaIds = list(range(len(self.freeBetaNames)))

        # List of values of the free beta parameters (those to be estimated)
        self.freeBetaValues = [
            self.allFreeBetas[x].initValue for x in self.freeBetaNames
        ]
        # List of values of the fixed beta parameters (those to be estimated)
        self.fixedBetaValues = [
            self.allFixedBetas[x].initValue for x in self.fixedBetaNames
        ]

        # Draws
        if self.requiresDraws():
            if database is None:
                error_msg = (
                    'An expression involving MonteCarlo integration '
                    'must be associated with a database.'
                )
                raise excep.biogemeError(error_msg)
            database.generateDraws(
                self.allDraws, self.drawNames, self.numberOfDraws
            )

        self.expression_prepared = True

    def createFunction(
        self,
        database=None,
        numberOfDraws=1000,
        gradient=True,
        hessian=True,
        bhhh=False,
    ):
        """Create a function based on the expression. The function takes as
            argument an array for the free parameters, and return the
            value of the function, the gradient, the hessian and the BHHH. The
            calculation of the derivatives is optional.

        :param database: database. If no database is provided, the
            expression must not contain any variable.
        :type database:  biogeme.database.Database

        :param numberOfDraws: number of draws if needed by Monte-Carlo
            integration.
        :type numberOfDraws: int

        :param gradient: if True, the gradient is calculated.
        :type gradient: bool

        :param hessian: if True, the hessian is calculated.
        :type hessian: bool

        :param bhhh: if True, the BHHH matrix is calculated.
        :type bhhh: bool

        :return: the function. It will return, in that order, the
            value of the function, the gradient, the hessian and the
            BHHH matrix. Only requested quantities will be
            returned. For instance, if the gradient and the BHHH
            matrix are requested, and not the hessian, the tuple that
            is returned is f, g, bhhh.

        :rtype: fct(np.array)

        :raise biogemeError: if gradient is False and hessian or BHHH is True.

        """
        if (hessian or bhhh) and not gradient:
            raise excep.biogemeError(
                'If the hessian or BHHH is calculated, so is the gradient. '
                'The provided parameters are inconsistent.'
            )

        if not self.expression_prepared:
            self._prepareFormulaForEvaluation(database)

        # variables = self.setOfVariables()
        # if variables:
        #    raise excep.biogemeError(
        #        'Functions can be generated only for simple expressions '
        #        'that do not involve any variable'
        #    )

        def my_function(x):
            if isinstance(x, (float, int, np.float64)):
                x = [float(x)]
            if len(x) != len(self.freeBetaValues):
                error_msg = (
                    f'Function is expecting an array lf length '
                    f'{len(self.freeBetaValues)}, not {len(x)}'
                )
                excep.biogemeError(error_msg)

            self.freeBetaValues = x
            f, g, h, b = self.getValueAndDerivatives(
                database=database,
                numberOfDraws=numberOfDraws,
                gradient=gradient,
                hessian=hessian,
                bhhh=bhhh,
                aggregation=True,
            )

            results = [f]
            if gradient:
                results.append(g)
                if hessian:
                    results.append(h)
                if bhhh:
                    results.append(b)
                return tuple(results)
            return f

        return my_function

    def getValue_c(
        self,
        betas=None,
        database=None,
        numberOfDraws=1000,
        aggregation=False,
    ):

        """Evaluation of the expression, without the derivatives

        :param betas: values of the free parameters
        :type betas: list(float)

        :param database: database. If no database is provided, the
            expression must not contain any variable.
        :type database:  biogeme.database.Database

        :param numberOfDraws: number of draws if needed by Monte-Carlo
            integration.
        :type numberOfDraws: int

        :param aggregation: if a database is provided, and this
            parameter is True, the expression is applied on each entry
            of the database, and all values are aggregated, so that
            the sum is returned. If False, the list of all values is returned.
        :type aggregation: bool

        :return: if a database is provided, a list where each entry is
            the result of applying the expression on one entry of the
            dsatabase. It returns a float.

        :rtype: np.array or float

        :raise biogemeError: if no database is given, and the number
            of returned values is different from one.
        """

        f, _, _, _ = self.getValueAndDerivatives(
            betas=betas,
            database=database,
            numberOfDraws=numberOfDraws,
            gradient=False,
            hessian=False,
            bhhh=False,
            aggregation=aggregation,
        )
        if database is None:
            if len(f) != 1:
                error_msg = 'Incorrect number of return values'
                raise excep.biogemeError(error_msg)
            return f[0]
        return f

    def getValueAndDerivatives(
        self,
        betas=None,
        database=None,
        numberOfDraws=1000,
        gradient=True,
        hessian=True,
        bhhh=True,
        aggregation=True,
    ):
        """Evaluation of the expression

        In Biogeme the complexity of some expressions requires a
        specific implementation, in C++. This function invokes the
        C++ code to evaluate the value of the expression for a
        series of entries in a database. Note that this function
        will generate draws if needed.

        :param betas: values of the free parameters
        :type betas: list(float)

        :param database: database. If no database is provided, the
            expression must not contain any variable.
        :type database:  biogeme.database.Database

        :param numberOfDraws: number of draws if needed by Monte-Carlo
            integration.
        :type numberOfDraws: int

        :param gradient: If True, the gradient is calculated.
        :type gradient: bool

        :param hessian: if True, the hessian is  calculated.
        :type hessian: bool

        :param bhhh: if True, the BHHH matrix is calculated.
        :type bhhh: bool

        :param aggregation: if a database is provided, and this
            parameter is True, the expression is applied on each entry
            of the database, and all values are aggregated, so that
            the sum is returned. If False, the list of all values is returned.
        :type aggregation: bool

        :return: if a database is provided, a list where each entry is
            the result of applying the expression on one entry of the
            dsatabase. It returns a float, a vector, and a matrix,
            depedending if derivatives are requested.

        :rtype: np.array or float, numpy.array, numpy.array

        :raise biogemeError: if no database is given and the
            expressions involves variables.

        :raise biogemeError: if gradient is False and hessian or BHHH is True.

        :raise biogemeError: if derivatives are asked, and the expression
            is not simple.

        :raise biogemeError: if the expression involves MonteCarlo integration,
           and no database is provided.
        """

        errors, warnings = self.audit(database)
        if warnings:
            if self.logger.screenLevel < 1:
                self.logger.setWarning()
                self.logger.warning('Logger status has been set to "warning"')
            self.logger.warning('\n'.join(warnings))
        if errors:
            error_msg = '\n'.join(errors)
            self.logger.warning(error_msg)
            raise excep.biogemeError(error_msg)

        if (hessian or bhhh) and not gradient:
            raise excep.biogemeError(
                'If the hessian or the BHHH matrix is calculated, '
                'so is the gradient. The provided parameters are inconsistent.'
            )
        if database is None:
            if variables := self.setOfVariables():
                raise excep.biogemeError(
                    f'No database is provided and the expression '
                    f'contains variables: {variables}'
                )

        self.numberOfDraws = numberOfDraws

        if not self.expression_prepared:
            self._prepareFormulaForEvaluation(database)
        if database is not None:
            self.cpp.setData(database.data)
            if self.embedExpression('PanelLikelihoodTrajectory'):
                if database.isPanel():
                    database.buildPanelMap()
                    self.cpp.setDataMap(database.individualMap)
                else:
                    error_msg = (
                        'The expression involves '
                        '"PanelLikelihoodTrajectory" '
                        'that requires panel data'
                    )
                    raise excep.biogemeError(error_msg)

        if betas is not None:
            self.freeBetaValues = [
                betas[x] if x in betas else self.allFreeBetas[x].initValue
                for x in self.freeBetaNames
            ]
            # List of values of the fixed beta parameters (those to be
            # estimated)
            self.fixedBetaValues = [
                betas[x] if x in betas else self.allFixedBetas[x].initValue
                for x in self.fixedBetaNames
            ]

        self.cpp.setExpression(self.getSignature())
        self.cpp.setFreeBetas(self.freeBetaValues)
        self.cpp.setFixedBetas(self.fixedBetaValues)
        self.cpp.setMissingData(self.missingData)

        if self.requiresDraws():
            if database is None:
                error_msg = (
                    'An expression involving MonteCarlo integration '
                    'must be associated with a database.'
                )
                raise excep.biogemeError(error_msg)
            self.cpp.setDraws(database.theDraws)

        self.cpp.calculate(
            gradient=gradient,
            hessian=hessian,
            bhhh=bhhh,
            aggregation=aggregation,
        )

        f, g, h, b = self.cpp.getResults()

        gres = g if gradient else None
        hres = h if hessian else None
        bhhhres = b if bhhh else None

        if aggregation:
            return (
                f[0],
                None if gres is None else g[0],
                None if hres is None else h[0],
                None if bhhhres is None else b[0],
            )
        return f, gres, hres, bhhhres

    def requiresDraws(self):
        """Checks if the expression requires draws

        :return: True if it requires draws.
        :rtype: bool
        """
        return self.embedExpression('MonteCarlo')

    def setOfBetas(self, free=True, fixed=False):
        """
        Extract the set of parameters from the expression.

        :param free: if True, the free parameters are included. Default: True.
        :type free: bool
        :param fixed: if True, the fixed parameters are included.
            Default: False.
        :type fixed: bool
        :return: returns a set with the beta parameters appearing in the
            expression.
        :rtype: set(biogeme.expressions.Expression)
        """
        s = set()
        for e in self.children:
            s = s.union(e.setOfBetas(free, fixed))
        return s

    def setOfVariables(self):
        """
        Extract the set of variables used in the expression.

        :return: returns a set with the variables appearing in the expression.
        :rtype: set(biogeme.expressions.Expression)
        """
        return set(self.dictOfVariables().keys())

    def dictOfBetas(self, free=True, fixed=False):
        """
        Extract the set of parameters from the expression.

        :param free: if True, the free parameters are included. Default: True.
        :type free: bool
        :param fixed: if True, the fixed parameters are included.
             Default: False.
        :type fixed: bool

        :return: a dict with the beta parameters appearing in the expression,
                 the keys being the names of the parameters.
        :rtype: dict(string:biogeme.expressions.Expression)

        """
        s = {}
        for e in self.children:
            d = e.dictOfBetas(free, fixed)
            s = dict(s, **d)
        return s

    def dictOfVariables(self):
        """Recursively extract the variables appearing in the expression, and
        store them in a dictionary.

        :return: returns a dict with the variables appearing in the
                 expression the keys being their names.
        :rtype: dict(string:biogeme.expressions.Expression)

        """
        s = {}
        for e in self.children:
            d = e.dictOfVariables()
            s = dict(s, **d)
        return s

    def dictOfRandomVariables(self):
        """Recursively extract the random variables appearing in the
        expression, and store them in a dictionary.

        :return: returns a dict with the random variables appearing in
                 the expression the keys being their names.

        :rtype: dict(string:biogeme.expressions.Expression)
        """
        s = {}
        for e in self.children:
            d = e.dictOfRandomVariables()
            s = dict(s, **d)
        return s

    def getElementaryExpression(self, name):
        """Return: an elementary expression from its name if it appears in the
        expression.

        :param name: name of the elementary expression.
        :type name: string

        :return: the expression if it exists. None otherwise.
        :rtype: biogeme.expressions.Expression
        """
        return next(
            (
                e.getElementaryExpression(name)
                for e in self.children
                if e.getElementaryExpression(name) is not None
            ),
            None,
        )

    def setRow(self, row):
        """Obsolete function.
        This function identifies the row of the database from which the
        values of the variables must be obtained.

        :param row: row from the database
        :type row: pandas.core.series.Serie

        :raise biogemeError: if the function is called, because it is obsolete.
        """
        raise excep.biogemeError("The function setRow is now obsolete.")

    def dictOfDraws(self):
        """Recursively extract the random variables
        (draws for Monte-Carlo)
        appearing in the expression, and store them in a dictionary.

        :return: dict where the keys are the random variables and the elements
             the type of draws
        :rtype: dict(string:string)
        """
        draws = {}
        for e in self.children:
            if d := e.dictOfDraws():
                draws = dict(draws, **d)
        return draws

    def setUniqueId(self, idsOfElementaryExpressions):
        """Provides a unique id to the elementary expressions.

        :param idsOfElementaryExpressions: dictionary mapping the name
              of the elementary expression with their id.
        :type idsOfElementaryExpressions: dict(string:int)

        """
        for e in self.children:
            e.setUniqueId(idsOfElementaryExpressions)

    def setSpecificIndices(
        self,
        indicesOfFreeBetas,
        indicesOfFixedBetas,
        indicesOfRandomVariables,
        indicesOfDraws,
    ):
        """Provides an index to all elementary expressions,
        specific to their type

        :param indicesOfFreeBetas: dictionary mapping the name of the
                               free betas with their index
        :type indicesOfFreeBetas: dict(string:int)

        :param indicesOfFixedBetas: dictionary mapping the name of the
                                fixed betas with their index
        :type indicesOfFixedBetas: dict(string:int)

        :param indicesOfRandomVariables: dictionary mapping the name of the
                                random variables with their index
        :type indicesOfRandomVariables: dict(string:int)
        :param indicesOfDraws: dictionary mapping the name of the draws with
                            their index
        :type indicesOfDraws: dict(string:int)

        """
        for e in self.children:
            e.setSpecificIndices(
                indicesOfFreeBetas,
                indicesOfFixedBetas,
                indicesOfRandomVariables,
                indicesOfDraws,
            )

    def setVariableIndices(self, indicesOfVariables):
        """
        Provide an index to all variables

        :param indicesOfVariables: dictionary mapping the name of the
                                variables with their index
        :type indicesOfVariables: dict(string:int)

        """
        for e in self.children:
            e.setVariableIndices(indicesOfVariables)

    def getClassName(self):
        """
        Obtain the name of the top class of the expression structure

        :return: the name of the class
        :rtype: string
        """
        return type(self).__name__

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the signatures of all the children expressions,
            2. the name of the expression between < >
            3. the id of the expression between { }
            4. the number of children between ( )
            5. the ids of each children, preceeded by a comma.

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
            \\frac{\\exp(-\\beta_2 V_2) }
            { \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                 (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)

        """
        listOfSignatures = []
        for e in self.children:
            listOfSignatures += e.getSignature()
        mysignature = f'<{self.getClassName()}>'
        mysignature += f'{{{id(self)}}}'
        mysignature += f'({len(self.children)})'
        for e in self.children:
            mysignature += f',{id(e)}'
        listOfSignatures += [mysignature.encode()]
        return listOfSignatures

    def isContainedIn(self, t):
        """Check if the expression is contained in an expression of type t.

        Typically, this would be used to check that a bioDraws
        expression is contained in a MonteCarlo expression. If not, it
        cannot be evaluated.

        :return: True if the expression is contained in an expression
            of type t.
        :rtype: bool.

        See: :func:`biogeme.expressions.Expression.embedExpression`
        """
        if self.parent is None:
            return False
        if self.parent.getClassName() == t:
            return True
        return self.parent.isContainedIn(t)

    def embedExpression(self, t):
        """Check if the expression contains an expression of type t.

        Typically, this would be used to check that a MonteCarlo
        expression contains a bioDraws expression.

        :return: True if the expression contains an expression of type t.
        :rtype: bool

        See: :func:`biogeme.expressions.Expression.isContainedIn`
        """
        if self.getClassName() == t:
            return True
        return any(e.embedExpression(t) for e in self.children)

    def countPanelTrajectoryExpressions(self):
        """Count the number of times the PanelLikelihoodTrajectory
        is used in the formula. It should trigger an error if it
        is used more than once.

        :return: number of times the PanelLikelihoodTrajectory
            is used in the formula
        :rtype: int
        """
        return sum(e.countPanelTrajectoryExpressions() for e in self.children)

    def audit(self, database=None):
        """Performs various checks on the expressions.

        :param database: database object
        :type database: biogeme.database.Database

        :return: tuple listOfErrors, listOfWarnings
        :rtype: list(string), list(string)
        """
        listOfErrors = []
        listOfWarnings = []

        for e in self.children:
            err, war = e.audit(database)
            listOfErrors += err
            listOfWarnings += war
        return listOfErrors, listOfWarnings

    def changeInitValues(self, betas):
        """Modifies the initial values of the Beta parameters.

        The fact that the parameters are fixed or free is irrelevant here.

        :param betas: dictionary where the keys are the names of the
                      parameters, and the values are the new value for
                      the parameters.
        :type betas: dict(string:float)
        """

        for e in self.children:
            e.changeInitValues(betas)


class BinaryOperator(Expression):
    """
    Base class for arithmetic expressions that are binary operators.
    This expression is the result of the combination of two expressions,
    typically addition, substraction, multiplication or division.
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.

        """
        Expression.__init__(self)
        if isNumeric(left):
            self.left = Numeric(left)  #: left parent
        elif isinstance(left, Expression):
            self.left = left
        else:
            raise excep.biogemeError(
                f'This is not a valid expression: {left}'
            )
        if isNumeric(right):
            self.right = Numeric(right)  #: right parent
        elif isinstance(right, Expression):
            self.right = right
        else:
            raise excep.biogemeError(
                f'This is not a valid expression: {right}'
            )
        self.left.parent = self
        self.right.parent = self
        self.children.append(self.left)
        self.children.append(self.right)


class Plus(BinaryOperator):
    """
    Addition expression
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} + {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return self.left.getValue() + self.right.getValue()


class Minus(BinaryOperator):
    """
    Substraction expression
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} - {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return self.left.getValue() - self.right.getValue()


class Times(BinaryOperator):
    """
    Multiplication expression
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression

        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} * {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return self.left.getValue() * self.right.getValue()


class Divide(BinaryOperator):
    """
    Division expression
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} / {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return self.left.getValue() / self.right.getValue()


class Power(BinaryOperator):
    """
    Power expression
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} ** {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return self.left.getValue() ** self.right.getValue()


class bioMin(BinaryOperator):
    """
    Minimum of two expressions
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'bioMin({self.left}, {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        if self.left.getValue() <= self.right.getValue():
            return self.left.getValue()

        return self.right.getValue()


class bioMax(BinaryOperator):
    """
    Maximum of two expressions
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'bioMax({self.left}, {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        if self.left.getValue() >= self.right.getValue():
            return self.left.getValue()

        return self.right.getValue()


class And(BinaryOperator):
    """
    Logical and
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression

        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} and {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        if self.left.getValue() == 0.0:
            return 0.0
        return 0.0 if self.right.getValue() == 0.0 else 1.0


class Or(BinaryOperator):
    """
    Logical or
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} or {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        if self.left.getValue() != 0.0:
            return 1.0
        return 1.0 if self.right.getValue() != 0.0 else 0.0


class Equal(BinaryOperator):
    """
    Logical equal
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} == {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return 1 if self.left.getValue() == self.right.getValue() else 0


class NotEqual(BinaryOperator):
    """
    Logical not equal
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} != {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return 1 if self.left.getValue() != self.right.getValue() else 0


class LessOrEqual(BinaryOperator):
    """
    Logical less or equal
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression

        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} <= {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return 1 if self.left.getValue() <= self.right.getValue() else 0


class GreaterOrEqual(BinaryOperator):
    """
    Logical greater or equal
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} >= {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return 1 if self.left.getValue() >= self.right.getValue() else 0


class Less(BinaryOperator):
    """
    Logical less
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} < {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return 1 if self.left.getValue() < self.right.getValue() else 0


class Greater(BinaryOperator):
    """
    Logical greater
    """

    def __init__(self, left, right):
        """Constructor

        :param left: first arithmetic expression
        :type left: biogeme.expressions.Expression

        :param right: second arithmetic expression
        :type right: biogeme.expressions.Expression
        """
        BinaryOperator.__init__(self, left, right)

    def __str__(self):
        return f'({self.left} > {self.right})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return 1 if self.left.getValue() > self.right.getValue() else 0


class UnaryOperator(Expression):
    """
    Base class for arithmetic expressions that are unary operators.

    Such an expression is the result of the modification of another
    expressions, typically changing its sign.
    """

    def __init__(self, child):
        """Constructor

        :param child: first arithmetic expression
        :type child: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.

        """
        Expression.__init__(self)
        if isNumeric(child):
            self.child = Numeric(child)  #: child
        elif isinstance(child, Expression):
            self.child = child
        else:
            raise excep.biogemeError(
                f'This is not a valid expression: {child}'
            )
        self.child.parent = self
        self.children.append(self.child)


class UnaryMinus(UnaryOperator):
    """
    Unary minus expression
    """

    def __init__(self, child):
        """Constructor

        :param child: first arithmetic expression
        :type child: biogeme.expressions.Expression
        """
        UnaryOperator.__init__(self, child)

    def __str__(self):
        return f'(-{self.child})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return -self.child.getValue()


class MonteCarlo(UnaryOperator):
    """
    Monte Carlo integration
    """

    def __init__(self, child):
        """Constructor

        :param child: arithmetic expression
        :type child: biogeme.expressions.Expression
        """
        UnaryOperator.__init__(self, child)

    def __str__(self):
        return f'MonteCarlo({self.child})'

    def audit(self, database=None):
        """Performs various checks on the expressions.

        :param database: database object
        :type database: biogeme.database.Database

        :return: tuple listOfErrors, listOfWarnings
        :rtype: list(string), list(string)

        """
        listOfErrors, listOfWarnings = self.child.audit(database)
        if database is None:
            if self.child.embedExpression('PanelLikelihoodTrajectory'):
                theWarning = (
                    'The formula contains a PanelLikelihoodTrajectory '
                    'expression, and no database is given'
                )
                listOfWarnings.append(theWarning)
        elif database.isPanel() and not self.child.embedExpression(
                'PanelLikelihoodTrajectory'
            ):
            theError = (
                f'As the database is panel, the argument '
                f'of MonteCarlo must contain a'
                f' PanelLikelihoodTrajectory: {self}'
            )
            listOfErrors.append(theError)

        if not self.child.embedExpression('bioDraws'):
            theError = (
                f'The argument of MonteCarlo must contain a'
                f' bioDraws: {self}'
            )
            listOfErrors.append(theError)
        if self.child.embedExpression('MonteCarlo'):
            theError = (
                f'It is not possible to include a MonteCarlo '
                f'statement in another one: {self}'
            )
            listOfErrors.append(theError)
        return listOfErrors, listOfWarnings


class bioNormalCdf(UnaryOperator):
    """
    Cumulative Distribution Function of a normal random variable
    """

    def __init__(self, child):
        """Constructor

        :param child: first arithmetic expression
        :type child: biogeme.expressions.Expression
        """
        UnaryOperator.__init__(self, child)

    def __str__(self):
        return f'bioNormalCdf({self.child})'


class PanelLikelihoodTrajectory(UnaryOperator):
    """
    Likelihood of a sequences of observations for the same individual
    """

    def __init__(self, child):
        """Constructor

        :param child: first arithmetic expression
        :type child: biogeme.expressions.Expression
        """
        UnaryOperator.__init__(self, child)

    def __str__(self):
        return f'PanelLikelihoodTrajectory({self.child})'

    def countPanelTrajectoryExpressions(self):
        """Count the number of times the PanelLikelihoodTrajectory
        is used in the formula.
        """
        return 1 + self.child.countPanelTrajectoryExpressions()

    def audit(self, database=None):
        """Performs various checks on the expressions.

        :param database: database object
        :type database: biogeme.database.Database

        :return: tuple listOfErrors, listOfWarnings
        :rtype: list(string), list(string)

        """
        listOfErrors, listOfWarnings = self.child.audit(database)
        if not database.isPanel():
            theError = (
                f'Expression PanelLikelihoodTrajectory can '
                f'only be used with panel data. Use the statement '
                f'database.panel("IndividualId") to declare the '
                f'panel structure of the data: {self}'
            )
            listOfErrors.append(theError)
        return listOfErrors, listOfWarnings


class exp(UnaryOperator):
    """
    exponential expression
    """

    def __init__(self, child):
        """Constructor

        :param child: first arithmetic expression
        :type child: biogeme.expressions.Expression
        """
        UnaryOperator.__init__(self, child)

    def __str__(self):
        return f'exp({self.child})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return np.exp(self.child.getValue())


class log(UnaryOperator):
    """
    logarithm expression
    """

    def __init__(self, child):
        """Constructor

        :param child: first arithmetic expression
        :type child: biogeme.expressions.Expression
        """
        UnaryOperator.__init__(self, child)

    def __str__(self):
        return f'log({self.child})'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return np.log(self.child.getValue())


class Derive(UnaryOperator):
    """
    Derivative with respect to an elementary expression
    """

    def __init__(self, child, name):
        """Constructor

        :param child: first arithmetic expression
        :type child: biogeme.expressions.Expression
        """
        UnaryOperator.__init__(self, child)
        # Name of the elementary expression by which the derivative is taken
        self.elementaryName = name
        # Unique ID of the expression
        self.elementaryIndex = None

    def setUniqueId(self, idsOfElementaryExpressions):
        """
        Provides a unique id to the elementary expressions.

        :param idsOfElementaryExpressions: dictionary mapping the name
                of the elementary expression with their id.
        :type idsOfElementaryExpressions: dict(string:int)

        :raise biogemeError: if no index is available for an expression.
        """
        if self.elementaryName in idsOfElementaryExpressions:
            self.elementaryIndex = idsOfElementaryExpressions[
                self.elementaryName
            ]
        else:
            error_msg = (
                f'No index is available for elementary '
                f'expression {self.elementaryName}.'
            )
            raise excep.biogemeError(error_msg)
        self.child.setUniqueId(idsOfElementaryExpressions)

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the signatures of the child expression,
            2. the name of the expression between < >
            3. the id of the expression between { }
            4. the id of the child, preceeded by a comma.

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
           \\frac{\\exp(-\\beta_2 V_2) }{ \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)
        """
        listOfSignatures = []
        listOfSignatures += self.child.getSignature()
        mysignature = f'<{self.getClassName()}>'
        mysignature += f'{{{id(self)}}}'
        mysignature += f',{id(self.child)}'
        mysignature += f',{self.elementaryIndex}'
        listOfSignatures += [mysignature.encode()]
        return listOfSignatures

    def __str__(self):
        return 'Derive({self.child}, "{self.elementName}")'


class Integrate(UnaryOperator):
    """
    Numerical integration
    """

    def __init__(self, child, name):
        """Constructor

        :param child: first arithmetic expression
        :type child: biogeme.expressions.Expression
        :param name: name of the random variable for the integration.
        :type name: string
        """
        UnaryOperator.__init__(self, child)
        self.randomVariableName = name
        self.randomVariableIndex = None

    def audit(self, database=None):
        """Performs various checks on the expressions.

        :param database: database object
        :type database: biogeme.database.Database

        :return: tuple listOfErrors, listOfWarnings
        :rtype: list(string), list(string)

        """
        listOfErrors, listOfWarnings = self.child.audit(database)
        if not self.child.embedExpression('RandomVariable'):
            theError = (
                f'The argument of Integrate must contain a '
                f'RandomVariable: {self}'
            )
            listOfErrors.append(theError)
        return listOfErrors, listOfWarnings

    def setUniqueId(self, idsOfElementaryExpressions):
        """Provides a unique id to the elementary expressions. Overloads the
        generic function

        :param idsOfElementaryExpressions: dictionary mapping the name of
                the elementary expression with their id.
        :type idsOfElementaryExpressions: dict(string:int)

        :raise biogemeError: if no index is available for a random variable.
        """
        if self.randomVariableName in idsOfElementaryExpressions:
            self.randomVariableIndex = idsOfElementaryExpressions[
                self.randomVariableName
            ]
        else:
            error_msg = (
                f'No index is available for random variable '
                f'{self.randomVariableName}.'
            )
            raise excep.biogemeError(error_msg)
        self.child.setUniqueId(idsOfElementaryExpressions)

    def setSpecificIndices(
        self,
        indicesOfFreeBetas,
        indicesOfFixedBetas,
        indicesOfRandomVariables,
        indicesOfDraws,
    ):
        """
        Provide an index to all elementary expressions, specific to their type
        Overloads the generic function.

        :param indicesOfFreeBetas: dictionary mapping the name of the
                               free betas with their index
        :type indicesOfFreeBetas: dict(string:int)

        :param indicesOfFixedBetas: dictionary mapping the name of the
                                fixed betas with their index
        :type indicesOfFixedBetas: dict(string:int)

        :param indicesOfRandomVariables: dictionary mapping the name of the
                                random variables with their index
        :type indicesOfRandomVariables: dict(string:int)
        :param indicesOfDraws: dictionary mapping the name of the draws with
                            their index
        :type indicesOfDraws: dict(string:int)

        :raise biogemeError: if no index is available for a random variable.

        """
        if self.randomVariableName in indicesOfRandomVariables:
            self.randomVariableIndex = indicesOfRandomVariables[
                self.randomVariableName
            ]
        else:
            error_msg = (
                f'No index is available for random variable '
                f'{self.randomVariableName}. Known random variables:'
                f' {indicesOfRandomVariables.keys()}'
            )
            raise excep.biogemeError(error_msg)
        self.child.setSpecificIndices(
            indicesOfFreeBetas,
            indicesOfFixedBetas,
            indicesOfRandomVariables,
            indicesOfDraws,
        )

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the signatures of the child expression,
            2. the name of the expression between < >
            3. the id of the expression between { }, preceeded by a comma
            4. the id of the children, preceeded by a comma
            5. the index of the randon variable, preceeded by a comma

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
             \\frac{\\exp(-\\beta_2 V_2) }
             { \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                 (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)
        """
        listOfSignatures = []
        listOfSignatures += self.child.getSignature()
        mysignature = f'<{self.getClassName()}>'
        mysignature += f'{{{id(self)}}}'
        mysignature += f',{id(self.child)}'
        mysignature += f',{self.randomVariableIndex}'
        listOfSignatures += [mysignature.encode()]
        return listOfSignatures

    def __str__(self):
        return f'Integrate({self.child}, "{self.randomVariableName}")'


class Elementary(Expression):
    """Elementary expression.

    It is typically defined by a name appearing in an expression. It
    can be a variable (from the database), or a parameter (fixed or to
    be estimated using maximum likelihood), a random variable for
    numrerical integration, or Monte-Carlo integration.

    """

    def __init__(self, name):
        """Constructor

        :param name: name of the elementary experession.
        :type name: string

        """
        Expression.__init__(self)
        self.name = name  #: name of the elementary expressiom

        self.uniqueId = None
        """The id should be unique for all elementary expressions
        appearing in a given set of formulas.
        """

    def __str__(self):
        """string method

        :return: name of the expression
        :rtype: str
        """
        return self.name

    def getElementaryExpression(self, name):
        """

        :return: an elementary expression from its name if it appears in the
            expression. None otherwise.
        :rtype: biogeme.Expression
        """
        return self if self.name == name else None

    def setUniqueId(self, idsOfElementaryExpressions):
        """
        Provides a unique id to the elementary expressions. Overloads the
        generic function

        :param idsOfElementaryExpressions: dictionary mapping the name
              of the elementary expression with their id.
        :type idsOfElementaryExpressions: dict(string:int)

        :raise biogemeError: if no index is available for an expression.
        """
        if self.name in idsOfElementaryExpressions:
            self.uniqueId = idsOfElementaryExpressions[self.name]
            if not isinstance(self.uniqueId, int):
                error_msg = (
                    f'An integer is required as an ID for [{self.name}]. '
                    f'The value [{self.uniqueId}] is of type '
                    f'{type(self.uniqueId)}'
                )
                raise excep.biogemeError(error_msg)

        else:
            error_msg = (
                f'No index is available for expression {self.name}.'
                f' List of available indices: '
                f'{[n for n, i in idsOfElementaryExpressions.items() ]}'
            )
            raise excep.biogemeError(error_msg)


class bioDraws(Elementary):
    """
    Draws for Monte-Carlo integration
    """

    def __init__(self, name, drawType):
        """Constructor

        :param name: name of the random variable with a series of draws.
        :type name: string
        :param drawType: type of draws.
        :type drawType: string
        """
        Elementary.__init__(self, name)
        self.drawType = drawType
        self.drawId = None

    def __str__(self):
        return f'bioDraws("{self.name}", "{self.drawType}")'

    def setSpecificIndices(
        self,
        indicesOfFreeBetas,
        indicesOfFixedBetas,
        indicesOfRandomVariables,
        indicesOfDraws,
    ):
        """
        Provide an index to all elementary expressions, specific to their type
        Overloads the generic function.

        :param indicesOfFreeBetas: dictionary mapping the name of the
                               free betas with their index
        :type indicesOfFreeBetas: dict(string:int)

        :param indicesOfFixedBetas: dictionary mapping the name of the
                                fixed betas with their index
        :type indicesOfFixedBetas: dict(string:int)

        :param indicesOfRandomVariables: dictionary mapping the name of the
                                random variables with their index
        :type indicesOfRandomVariables: dict(string:int)
        :param indicesOfDraws: dictionary mapping the name of the draws with
                            their index
        :type indicesOfDraws: dict(string:int)

        :raise biogemeError: if no index is available for one draw type.
        """
        if indicesOfDraws is None:
            error_msg = (
                f'No index is available for draw {self.drawType}.'
                f' Actually, no draws have been identified.'
            )
            raise excep.biogemeError(error_msg)

        if self.name in indicesOfDraws:
            self.drawId = indicesOfDraws[self.name]
        else:
            error_msg = (
                f'No index is available for draw {self.drawType}.'
                f' Known types of draws: {indicesOfDraws.keys()}'
            )
            raise excep.biogemeError(error_msg)

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the name of the expression between < >
            2. the id of the expression between { }, preceeded by a comma
            3. the name of the draws
            4. the unique ID (preceeded by a comma),
            5. the draw ID (preceeded by a comma).

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
           \\frac{\\exp(-\\beta_2 V_2) }{ \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)

        :raise biogeme.exceptions.biogemeError: if no id has been defined for
            elementary expression
        :raise biogeme.exceptions.biogemeError: if no id has been defined for
            draw
        """
        if self.uniqueId is None:
            error_msg = (
                f'No id has been defined for elementary '
                f'expression {self.name}.'
            )
            raise excep.biogemeError(error_msg)
        if self.drawId is None:
            error_msg = f'No id has been defined for draw {self.name}.'
            raise excep.biogemeError(error_msg)
        signature = f'<{self.getClassName()}>'
        signature += f'{{{id(self)}}}'
        signature += f'"{self.name}",{self.uniqueId},{self.drawId}'
        return [signature.encode()]

    def dictOfDraws(self):
        """Recursively extract the random variables
        (draws for Monte-Carlo).  Overloads the generic function.
        appearing in the expression, and store them in a dictionary.

        :return: dict where the keys are the random variables and the
                 elements the type of draws. Here, contains only one element.
        :rtype: dict(string:string)
        """
        return {self.name: self.drawType}

    def setDrawIndex(self, idsOfDraws):
        """
        Provide an index to a series of draw for a random variable. Overload
        the generic function.

        :param idsOfDraws: dictionary mapping the name of the draws with
            their id.
        :type idsOfDraws: dict(string:int)

        :raise biogemeError: if no id is available for a draw.
        """
        if self.name in idsOfDraws:
            self.drawId = idsOfDraws[self.name]
        else:
            error_msg = (
                f'No id is available for draw {self.name}. '
                f'List of available indices: '
                f'{[n for n, i in idsOfDraws.items()]}'
            )
            raise excep.biogemeError(error_msg)

    def audit(self, database=None):
        """Performs various checks on the expressions.

        :param database: database object
        :type database: biogeme.database.Database

        :return: tuple listOfErrors, listOfWarnings
        :rtype: list(string), list(string)

        """
        listOfErrors = []
        listOfWarnings = []
        if not self.isContainedIn('MonteCarlo'):
            theError = (
                f'bioDraws expression must be embedded into a '
                f'MonteCarlo: {self}'
            )
            listOfErrors.append(theError)
        return listOfErrors, listOfWarnings


class Numeric(Expression):
    """
    Numerical expression for a simple number
    """

    def __init__(self, value):
        """Constructor

        :param value: numerical value
        :type value: float
        """
        Expression.__init__(self)
        self.value = value  #: numeric value

    def __str__(self):
        return f'`{str(self.value)}`'

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return self.value

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the name of the expression between < >
            2. the id of the expression between { }
            3. the value, preceeded by a comma.

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
           \\frac{\\exp(-\\beta_2 V_2) }{ \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)
        """
        signature = f'<{self.getClassName()}>'
        signature += f'{{{id(self)}}}'
        signature += f',{self.value}'
        return [signature.encode()]


class Variable(Elementary):
    """Explanatory variable

    This represents the explanatory variables of the choice
    model. Typically, they come from the data set.
    """

    def __init__(self, name):
        """Constructor

        :param name: name of the variable.
        :type name: string
        """
        Elementary.__init__(self, name)
        # Index of the variable
        self.variableId = None

    def getValue(self):
        """The evaluation of a Variable requires a database. Therefore, this
            function triggers an exception.

        :raise biogemeError: each time the function is calles

        """
        error_msg = (
            f'Evaluating Variable {self.name} requires a database. Use the '
            f'function getValue_c instead.'
        )
        raise excep.biogemeError(error_msg)

    def dictOfVariables(self):
        """Recursively extract the variables appearing in the expression, and
        store them in a dictionary.

        Overload the generic function.

        :return: returns a dict with the variables appearing in the
               expression the keys being their names.
               Here, it contains only one element.
        :rtype: dict(string:biogeme.expressions.Expression)

        """
        return {self.name: self}

    def audit(self, database=None):
        """Performs various checks on the expressions.

        :param database: database object
        :type database: biogeme.database.Database

        :return: tuple listOfErrors, listOfWarnings
        :rtype: list(string), list(string)

        :raise biogemeError: if no database is provided.

        :raise biogemeError: if the name of the variable does not appear
            in the database.
        """
        listOfErrors = []
        listOfWarnings = []
        if database is None:
            raise excep.biogemeError(
                'The database must be provided to audit the variable.'
            )
        if self.name not in database.data.columns:
            theError = f'Variable {self.name} not found in the database.'
            listOfErrors.append(theError)
        return listOfErrors, listOfWarnings

    def setVariableIndices(self, indicesOfVariables):
        """
        Provide an index to all variables

        :param indicesOfVariables: dictionary mapping the name of the
                                variables with their index
        :type indicesOfVariables: dict(string:int)

        :raise biogemeError: if no index is provided for the variable
        """
        try:
            self.variableId = indicesOfVariables[self.name]
        except KeyError as e:
            error_msg = f'No ID has been provided for variable {self.name}'
            raise excep.biogemeError(error_msg) from e

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the name of the expression between < >
            2. the id of the expression between { }
            3. the name of the variable,
            4. the unique ID, preceeded by a comma.
            5. the variabvle ID, preceeded by a comma.

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
         \\frac{\\exp(-\\beta_2 V_2) }{ \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)

        :raise biogeme.exceptions.biogemeError: if no id has been defined for
            elementary expression
        :raise biogeme.exceptions.biogemeError: if no id has been defined for
            variable
        """
        if self.uniqueId is None:
            error_msg = (
                f'No id has been defined for elementary expression '
                f'{self.name}.'
            )
            raise excep.biogemeError(error_msg)
        if self.variableId is None:
            error_msg = f'No id has been defined for variable {self.name}.'
            raise excep.biogemeError(error_msg)
        signature = f'<{self.getClassName()}>'
        signature += f'{{{id(self)}}}'
        signature += f'"{self.name}",{self.uniqueId},{self.variableId}'
        return [signature.encode()]


class DefineVariable(Variable):
    """Expression that defines a new variable and add a column in the database.

    This expression allows the use to define a new variable that
    will be added to the database. It avoids that it is
    recalculated each time it is needed.
    """

    def __init__(self, name, expression, database):
        """Constructor

        :param name: name of the variable.
        :type name: string
        :param expression: formula that defines the variable
        :param type:  biogeme.expressions.Expression
        :param database: object identifying the database.
        :type database: biogeme.database.Database

        :raise biogemeError: if the expression is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        Variable.__init__(self, name)
        if isNumeric(expression):
            database.addColumn(Numeric(expression), name)
        elif isinstance(expression, Expression):
            database.addColumn(expression, name)
        else:
            raise excep.biogemeError(
                f'This is not a valid expression: {expression}'
            )


class RandomVariable(Elementary):
    """
    Random variable for numerical integration
    """

    def __init__(self, name):
        """Constructor

        :param name: name of the random variable involved in the integration.
        :type name: string.
        """
        Elementary.__init__(self, name)
        # Index of the random variable
        self.rvId = None

    def audit(self, database=None):
        """Performs various checks on the expressions.

        :param database: database object
        :type database: biogeme.database.Database

        :return: tuple listOfErrors, listOfWarnings
        :rtype: list(string), list(string)

        """
        listOfErrors = []
        listOfWarnings = []
        if not self.isContainedIn('Integrate'):
            theError = (
                f'RandomVariable expression must be embedded into '
                f'a integrate: {self}'
            )
            listOfErrors.append(theError)
        return listOfErrors, listOfWarnings

    def dictOfRandomVariables(self):
        """Recursively extract the random variables appearing in
        the expression, and store them in a dictionary.

        Overloads the generic function.

        :return: returns a dict with the random variables appearing in
                 the expression the keys being their names.

        :rtype: dict(string:biogeme.expressions.Expression)
        """
        return {self.name: self}

    def setSpecificIndices(
        self,
        indicesOfFreeBetas,
        indicesOfFixedBetas,
        indicesOfRandomVariables,
        indicesOfDraws,
    ):
        """
        Provide an index to all elementary expressions, specific to their type
        Overloads the generic function.

        :param indicesOfFreeBetas: dictionary mapping the name of the
                               free betas with their index
        :type indicesOfFreeBetas: dict(string:int)

        :param indicesOfFixedBetas: dictionary mapping the name of the
                                fixed betas with their index
        :type indicesOfFixedBetas: dict(string:int)

        :param indicesOfRandomVariables: dictionary mapping the name of the
                                random variables with their index
        :type indicesOfRandomVariables: dict(string:int)
        :param indicesOfDraws: dictionary mapping the name of the draws with
                            their index
        :type indicesOfDraws: dict(string:int)

        :raise biogemeError: if no index is available for a random variable.
        """
        if indicesOfRandomVariables is None:
            error_msg = (
                f'No index is available for random variable {self.name}.'
                f' Actually, no random variable has been identified.'
            )
            raise excep.biogemeError(error_msg)
        if self.name in indicesOfRandomVariables:
            self.rvId = indicesOfRandomVariables[self.name]
        else:
            error_msg = (
                f'No index is available for random variable '
                f'{self.name}. Known random variables: '
                f'{indicesOfRandomVariables.keys()}'
            )
            raise excep.biogemeError(error_msg)

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the name of the expression between < >
            2. the id of the expression between { }
            3. the name of the random variable,
            4. the unique ID, preceeded by a comma,
            5. the ID of the random variable.

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
           \\frac{\\exp(-\\beta_2 V_2) }{ \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)

        :raise biogeme.exceptions.biogemeError: if no id has been defined for
            elementary expression
        :raise biogeme.exceptions.biogemeError: if no id has been defined for
            random variable
        """
        if self.uniqueId is None:
            error_msg = (
                f'No id has been defined for elementary '
                f'expression {self.name}.'
            )
            raise excep.biogemeError(error_msg)
        if self.rvId is None:
            error_msg = (
                f'No id has been defined for random variable {self.name}.'
            )
            raise excep.biogemeError(error_msg)

        signature = f'<{self.getClassName()}>'
        signature += f'{{{id(self)}}}'
        signature += f'"{self.name}",{self.uniqueId},{self.rvId}'
        return [signature.encode()]


class Beta(Elementary):
    """
    Unknown parameters to be estimated from data.
    """

    def __init__(self, name, value, lowerbound, upperbound, status):
        """Constructor

        :param name: name of the parameter.
        :type name: string
        :param value: default value.
        :type value: float
        :param lowerbound: if different from None, imposes a lower
          bound on the value of the parameter during the optimization.
        :type lowerbound: float
        :param upperbound: if different from None, imposes an upper
          bound on the value of the parameter during the optimization.
        :type upperbound: float
        :param status: if different from 0, the parameter is fixed to
          its default value, and not modified by the optimization algorithm.
        :type status: int

        :raise biogemeError: if the first parameter is not a str.

        :raise biogemeError: if the second parameter is not a int or a float.
        """

        if not isinstance(value, (int, float)):
            error_msg = (
                f'The second parameter for {name} must be '
                f'a float and not a {type(value)}: {value}'
            )
            raise excep.biogemeError(error_msg)
        if not isinstance(name, str):
            error_msg = (
                f'The first parameter must be a string and '
                f'not a {type(name)}: {name}'
            )
            raise excep.biogemeError(error_msg)
        Elementary.__init__(self, name)
        self.initValue = value
        self.lb = lowerbound
        self.ub = upperbound
        self.status = status
        self.betaId = None

    def __str__(self):
        return f'{self.name}({self.initValue})'

    def setOfBetas(self, free=True, fixed=False):
        """Extract the set of parameters from the expression. Overload the
        generic function.

        :param free: if True, the free parameters are included. Default: True.
        :type free: bool
        :param fixed: if True, the fixed parameters are included.
            Default: False.
        :type fixed: bool
        :return: returns a set with the beta parameters appearing in the
            expression.
        :rtype: set(biogeme.expressions.Expression)

        """
        if fixed and self.status != 0:
            return {self.name}

        return {self.name} if free and self.status == 0 else set()

    def setSpecificIndices(
        self,
        indicesOfFreeBetas,
        indicesOfFixedBetas,
        indicesOfRandomVariables,
        indicesOfDraws,
    ):
        """
        Provide an index to all elementary expressions, specific to their type

        :param indicesOfFreeBetas: dictionary mapping the name of the
                               free betas with their index
        :type indicesOfFreeBetas: dict(string:int)

        :param indicesOfFixedBetas: dictionary mapping the name of the
                                fixed betas with their index
        :type indicesOfFixedBetas: dict(string:int)

        :param indicesOfRandomVariables: dictionary mapping the name of the
                                random variables with their index
        :type indicesOfRandomVariables: dict(string:int)
        :param indicesOfDraws: dictionary mapping the name of the draws with
                            their index
        :type indicesOfDraws: dict(string:int)

        :raise biogemeError: if no index is available for one of the parameters

        """

        if self.status != 0:
            if indicesOfFixedBetas is None:
                error_msg = (
                    f'No index is available for fixed parameter '
                    f'{self.name}. Actually, no fixed parameter '
                    f'has been identified.'
                )
                raise excep.biogemeError(error_msg)
            if self.name in indicesOfFixedBetas:
                self.betaId = indicesOfFixedBetas[self.name]
            else:
                error_msg = (
                    f'No index is available for fixed parameter '
                    f'{self.name}. Known fixed parameters: '
                    '{indicesOfFixedBetas.keys()}'
                )
                raise excep.biogemeError(error_msg)
        else:
            if indicesOfFreeBetas is None:
                error_msg = (
                    f'No index is available for free parameter '
                    f'{self.name}. Actually, no free parameter '
                    f'has been identified.'
                )
                raise excep.biogemeError(error_msg)

            if self.name in indicesOfFreeBetas:
                self.betaId = indicesOfFreeBetas[self.name]
            else:
                error_msg = (
                    f'No index is available for free parameter '
                    f'{self.name}. Known free parameters: '
                    f'{indicesOfFreeBetas.keys()}'
                )
                raise excep.biogemeError(error_msg)

    def dictOfBetas(self, free=True, fixed=False):
        """Extract the set of parameters from the expression. Overload the
        generic function.

        :param free: if True, the free parameters are included. Default: True.
        :type free: bool
        :param fixed: if True, the fixed parameters are included.
             Default: False.
        :type fixed: bool

        :return: a dict with the beta parameters appearing in the expression,
                 the keys being the names of the parameters.
        :rtype: dict(string:biogeme.expressions.Expression)
        """
        if fixed and self.status != 0:
            return {self.name: self}

        return {self.name: self} if free and self.status == 0 else {}

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        return self.initValue

    def changeInitValues(self, betas):
        """Modifies the initial values of the Beta parameters.

        The fact that the parameters are fixed or free is irrelevant here.

        :param betas: dictionary where the keys are the names of the
                      parameters, and the values are the new value for
                      the parameters.
        :type betas: dict(string:float)
        """

        if self.name in betas:
            self.initValue = betas[self.name]

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the name of the expression between < >
            2. the id of the expression between { }
            3. the name of the parameter,
            4. the status between [ ]
            5. the unique ID,  preceeded by a comma
            6. the beta ID,  preceeded by a comma


        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
           \\frac{\\exp(-\\beta_2 V_2) }{ \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                 (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)

        :raise biogeme.exceptions.biogemeError: if no id has been defined for
            elementary expression
        :raise biogeme.exceptions.biogemeError: if no id has been defined for
            parameter
        """
        if self.uniqueId is None:
            error_msg = (
                f'No id has been defined for elementary '
                f'expression {self.name}.'
            )
            raise excep.biogemeError(error_msg)
        if self.betaId is None:
            raise excep.biogemeError(
                f'No id has been defined for parameter {self.name}.'
            )

        signature = f'<{self.getClassName()}>'
        signature += f'{{{id(self)}}}'
        signature += (
            f'"{self.name}"[{self.status}],{self.uniqueId},{self.betaId}'
        )
        return [signature.encode()]


class LogLogit(Expression):
    """Expression capturing the logit formula.

    It contains one formula for the target alternative, a dict of
    formula for the availabilities and a dict of formulas for the
    utilities

    """

    def __init__(self, util, av, choice):
        """Constructor

        :param util: dictionary where the keys are the identifiers of
                     the alternatives, and the elements are objects
                     defining the utility functions.

        :type util: dict(int:biogeme.expressions.Expression)

        :param av: dictionary where the keys are the identifiers of
                   the alternatives, and the elements are object of
                   type biogeme.expressions.Expression defining the
                   availability conditions. If av is None, all the
                   alternatives are assumed to be always available

        :type av: dict(int:biogeme.expressions.Expression)

        :param choice: formula to obtain the alternative for which the
                       logit probability must be calculated.
        :type choice: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        Expression.__init__(self)
        self.util = {}  #: dict of utility functions
        for i, e in util.items():
            if isNumeric(e):
                self.util[i] = Numeric(e)
            elif isinstance(e, Expression):
                self.util[i] = e
            else:
                raise excep.biogemeError(
                    f'This is not a valid expression: {e}'
                )
        self.av = {}  #: dict of availability formulas
        if av is None:
            self.av = {k: Numeric(1) for k, v in util.items()}
        else:
            for i, e in av.items():
                if isNumeric(e):
                    self.av[i] = Numeric(e)
                elif isinstance(e, Expression):
                    self.av[i] = e
                else:
                    raise excep.biogemeError(
                        f'This is not a valid expression: {e}'
                    )
        if isNumeric(choice):
            self.choice = Numeric(choice)
            """expression for the chosen alternative"""
        elif isinstance(choice, Expression):
            self.choice = choice

        else:
            raise excep.biogemeError(
                f'This is not a valid expression: {choice}'
            )
        self.choice.parent = self
        self.children.append(self.choice)
        for e in self.util.values():
            e.parent = self
            self.children.append(e)
        for e in self.av.values():
            e.parent = self
            self.children.append(e)

    def audit(self, database=None):
        """Performs various checks on the expressions.

        :param database: database object
        :type database: biogeme.database.Database

        :return: tuple listOfErrors, listOfWarnings
        :rtype: list(string), list(string)

        """
        listOfWarnings = []
        listOfErrors = []
        for e in self.children:
            err, war = e.audit(database)
            listOfErrors += err
            listOfWarnings += war

        if self.util.keys() != self.av.keys():
            theError = (
                'Incompatible list of alternatives in logit expression. '
            )
            consistent = False
            if myset := self.util.keys() - self.av.keys():
                mysetContent = ', '.join(f'{str(k)} ' for k in myset)
                theError += f'Id(s) used for utilities and not for availabilities: {mysetContent}'
            if myset := self.av.keys() - self.util.keys():
                mysetContent = ', '.join(f'{str(k)} ' for k in myset)
                theError += f' Id(s) used for availabilities and not for utilities: {mysetContent}'
            listOfErrors.append(theError)
        else:
            consistent = True
        listOfAlternatives = list(self.util)
        if database is None:
            choices = np.array([self.choice.getValue_c()])
        else:
            choices = database.valuesFromDatabase(self.choice)
        correctChoices = np.isin(choices, listOfAlternatives)
        indexOfIncorrectChoices = np.argwhere(~correctChoices)
        if indexOfIncorrectChoices.any():
            incorrectChoices = choices[indexOfIncorrectChoices]
            content = '-'.join(
                '{}[{}]'.format(*t)
                for t in zip(indexOfIncorrectChoices, incorrectChoices)
            )
            truncate = 100
            if len(content) > truncate:
                content = f'{content[:truncate]}...'
            theError = f'The choice variable [{self.choice}] does not correspond to a valid alternative for the following observations (rownumber[choice]): {content}'
            listOfErrors.append(theError)

        if consistent:
            if database is None:
                value_choice = self.choice.getValue_c()
                if value_choice not in self.av.keys():
                    theError = (
                        f'The chosen alternative [{value_choice}] '
                        f'is not available'
                    )
                    listOfErrors.append(theError)
            else:
                choiceAvailability = database.checkAvailabilityOfChosenAlt(
                    self.av, self.choice
                )
                indexOfUnavailableChoices = np.where(~choiceAvailability)[0]
                if indexOfUnavailableChoices.size > 0:
                    incorrectChoices = choices[indexOfUnavailableChoices]
                    content = '-'.join(
                        '{}[{}]'.format(*t)
                        for t in zip(
                            indexOfUnavailableChoices, incorrectChoices
                        )
                    )
                    truncate = 100
                    if len(content) > truncate:
                        content = f'{content[:truncate]}...'
                    theError = f'The chosen alternative [{self.choice}] is not available for the following observations (rownumber[choice]): {content}'
                    listOfWarnings.append(theError)

        return listOfErrors, listOfWarnings

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float

        :raise biogemeError: if the chosen alternative does not correspond
            to any of the utility functions

        :raise biogemeError: if the chosen alternative does not correspond
            to any of entry in the availability condition

        """
        choice = int(self.choice.getValue())
        if choice not in self.util:
            error_msg = (
                f'Alternative {choice} for not appear in the list '
                f'of utility functions: {self.util.keys()}'
            )
            raise excep.biogemeError(error_msg)
        if choice not in self.av:
            error_msg = (
                f'Alternative {choice} for not appear in the list '
                f'of availabilities: {self.av.keys()}'
            )
            raise excep.biogemeError(error_msg)
        if self.av[choice].getValue() == 0.0:
            return -np.log(0)
        Vchosen = self.util[choice].getValue()
        denom = 0.0
        for i, V in self.util.items():
            if self.av[i].getValue() != 0.0:
                denom += np.exp(V.getValue() - Vchosen)
        return -np.log(denom)

    def __str__(self):
        s = self.getClassName()
        s += '('
        first = True
        for i, e in self.util.items():
            if first:
                s += f'{int(i)}:{e}'
                first = False
            else:
                s += f', {int(i)}:{e}'
        s += ')'
        return s

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the signatures of all the children expressions,
            2. the name of the expression between < >
            3. the id of the expression between { }
            4. the number of alternatives between ( )
            5. the id of the expression for the chosen alternative, preceeded
               by a comma.
            6. for each alternative, separated by commas:

                 a. the number of the alternative, as defined by the user,
                 b. the id of the expression for the utility,
                 c. the id of the expression for the availability condition.

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
          \\frac{\\exp(-\\beta_2 V_2) }{ \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)
        """
        listOfSignatures = []
        for e in self.children:
            listOfSignatures += e.getSignature()
        signature = f'<{self.getClassName()}>'
        signature += f'{{{id(self)}}}'
        signature += f'({len(self.util)})'
        signature += f',{id(self.choice)}'
        for i, e in self.util.items():
            signature += f',{i},{id(e)},{id(self.av[i])}'
        listOfSignatures += [signature.encode()]
        return listOfSignatures


class _bioLogLogit(LogLogit):
    """log of logit formula

    This expression captures the logarithm of the logit formula. It
    contains one formula for the target alternative, a dict of formula
    for the availabilities and a dict of formulas for the utilities It
    uses only the C++ implementation.
    """


class _bioLogLogitFullChoiceSet(LogLogit):
    """This expression captures the logarithm of the logit formula, where
    all alternatives are supposed to be always available.

       It contains one formula for the target alternative and a dict of
       formulas for the utilities. It uses only the C++ implementation.

    """


class bioMultSum(Expression):
    """This expression returns the sum of several other expressions.

    It is a generalization of 'Plus' for more than two terms
    """

    def __init__(self, listOfExpressions):
        """Constructor

        :param listOfExpressions: list of objects representing the
                                     terms of the sum.

        :type listOfExpressions: list(biogeme.expressions.Expression)

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        Expression.__init__(self)
        if isinstance(listOfExpressions, dict):
            for e in listOfExpressions.values():
                if isNumeric(e):
                    theExpression = Numeric(e)
                    theExpression.parent = self
                    self.children.append(theExpression)
                else:
                    if not isinstance(e, Expression):
                        raise excep.biogemeError(
                            f'This is not a valid expression: {e}'
                        )
                    e.parent = self
                    self.children.append(e)
        elif isinstance(listOfExpressions, list):
            for e in listOfExpressions:
                if isNumeric(e):
                    theExpression = Numeric(e)
                    theExpression.parent = self
                    self.children.append(theExpression)
                else:
                    if not isinstance(e, Expression):
                        raise excep.biogemeError(
                            f'This is not a valid expression: {e}'
                        )
                    e.parent = self
                    self.children.append(e)
        else:
            raise excep.biogemeError(
                'Argument of bioMultSum must be a dict or a list.'
            )

    def getValue(self):

        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float
        """
        result = 0.0
        for e in self.children:
            result += e.getValue()
        return result

    def __str__(self):
        return 'bioMultSum(' + ', '.join([f'{e}' for e in self.children]) + ')'


class Elem(Expression):
    """This returns the element of a dictionary. The key is evaluated
    from an expression.
    """

    def __init__(self, dictOfExpressions, keyExpression):
        """Constructor

        :param dictOfExpressions: dict of objects with numerical keys.
        :type dictOfExpressions: dict(int: biogeme.expressions.Expression)

        :param keyExpression: object providing the key of the element
                              to be evaluated.
        :type keyExpression: biogeme.expressions.Expression

        :raise biogemeError: if one of the expressions is invalid, that is
            neither a numeric value or a
            biogeme.expressions.Expression object.
        """
        Expression.__init__(self)

        self.dictOfExpressions = {}  #: dict of expressions
        for k, v in dictOfExpressions.items():
            if isNumeric(v):
                self.dictOfExpressions[k] = Numeric(v)
            elif isinstance(v, Expression):
                self.dictOfExpressions[k] = v
            else:
                raise excep.biogemeError(
                    f'This is not a valid expression: {v}'
                )
            self.dictOfExpressions[k].parent = self
            self.children.append(self.dictOfExpressions[k])

        if isinstance(keyExpression, bool):
            self.keyExpression = Numeric(1) if keyExpression else Numeric(0)
        elif isNumeric(keyExpression):
            self.keyExpression = Numeric(keyExpression)
        elif isinstance(keyExpression, Expression):
            self.keyExpression = keyExpression  #: expression for the key
        else:
            raise excep.biogemeError(
                f'This is not a valid expression: {keyExpression}'
            )
        self.keyExpression.parent = self
        self.children.append(self.keyExpression)

    def getValue(self):
        """Evaluates the value of the expression

        :return: value of the expression
        :rtype: float

        :raise biogemeError: if the calcuated key is not present in
            the dictionary.
        """
        key = int(self.keyExpression.getValue())
        if key in self.dictOfExpressions:
            return self.dictOfExpressions[key].getValue()

        error_msg = (
            f'Key {key} is not present in the dictionary. '
            f'Available keys: {self.dictOfExpressions.keys()}'
        )
        raise excep.biogemeError(error_msg)

    def __str__(self):
        s = '{{'
        first = True
        for k, v in self.dictOfExpressions.items():
            if first:
                s += f'{k}:{v}'
                first = False
            else:
                s += f', {k}:{v}'
        s += f'}}[{self.keyExpression}]'
        return s

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the signature of the expression defining the key
            2. the signatures of all the children expressions,
            3. the name of the expression between < >
            4. the id of the expression between { }
            5. the number of elements between ( )
            6. the id of the expression defining the key
            7. for each element: the value of the key and the id
               of the expression, separated by commas.

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
           \\frac{\\exp(-\\beta_2 V_2) }{ \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)
        """
        listOfSignatures = []
        listOfSignatures += self.keyExpression.getSignature()
        for i, e in self.dictOfExpressions.items():
            listOfSignatures += e.getSignature()
        signature = '<{}>'.format(self.getClassName())
        signature += '{{{}}}'.format(id(self))
        signature += '({})'.format(len(self.dictOfExpressions))
        signature += ',{}'.format(id(self.keyExpression))
        for i, e in self.dictOfExpressions.items():
            signature += f',{i},{id(e)}'
        listOfSignatures += [signature.encode()]
        return listOfSignatures


class bioLinearUtility(Expression):
    """When the utility function is linear, it is expressed as a list of
    terms, where a parameter multiplies a variable.
    """

    def __init__(self, listOfTerms):
        """Constructor

        :param listOfTerms: a list of tuple. Each tuple contains first
             a beta parameter, second the name of a variable.
        :type listOfTerms: list(biogeme.expressions.Expression,
            biogeme.expressions.Expression)

        :raises biogeme.exceptions.biogemeError: if the object is not
                        a list of tuples (parameter, variable)

        """
        Expression.__init__(self)

        theError = ""
        first = True

        for b, v in listOfTerms:
            if not isinstance(b, Beta):
                if first:
                    theError += (
                        'Each element of the bioLinearUtility '
                        'must be a tuple (parameter, variable). '
                    )
                    first = False
                theError += f' Expression {b} is not a parameter.'
            if not isinstance(v, Variable):
                if first:
                    theError += (
                        'Each element of the list should be '
                        'a tuple (parameter, variable).'
                    )
                    first = False
                theError += f' Expression {v} is not a variable.'
        if not first:
            raise excep.biogemeError(theError)

        self.betas, self.variables = zip(*listOfTerms)

        self.betas = list(self.betas)  #: list of parameters

        self.variables = list(self.variables)  #: list of variables

        self.listOfTerms = list(zip(self.betas, self.variables))
        """ List of terms """

        self.children += self.betas + self.variables

    def __str__(self):
        return ' + '.join([f'{b} * {x}' for b, x in self.listOfTerms])

    def setOfBetas(self, free=True, fixed=False):
        """
        Extract the set of parameters from the expression.

        :param free: if True, the free parameters are included. Default: True.
        :type free: bool
        :param fixed: if True, the fixed parameters are included.
             Default: False.
        :type fixed: bool
        :return: returns a set with the beta parameters appearing in the
            expression.
        :rtype: set(biogeme.expressions.Expression)

        """
        if free:
            return set(self.betas)

        return set()

    def dictOfBetas(self, free=True, fixed=False):
        """
        Extract the set of parameters from the expression.

        :param free: if True, the free parameters are included. Default: True.
        :type free: bool
        :param fixed: if True, the fixed parameters are included.
            Default: False.
        :type fixed: bool

        :return: a dict with the beta parameters appearing
             in the expression, the keys being the names of the parameters.
        :rtype: dict(string:biogeme.expressions.Expression)

        """
        freenames = {x.name: x for x in self.betas if x.status == 0}
        fixednames = {x.name: x for x in self.betas if x.status != 0}
        if free and fixed:
            allnames = {**freenames, **fixednames}
            return allnames
        if free:
            return freenames
        if fixed:
            return fixednames
        return dict()

    def dictOfVariables(self):
        """Recursively extract the variables appearing in the expression, and
        store them in a dictionary.

        Overloads the generic function.

        :return: returns a dict with the variables appearing
                 in the expression the keys being their names.
        :rtype: dict(string:biogeme.expressions.Expression)

        """
        return {x.name: x for x in self.variables}

    def dictOfRandomVariables(self):
        """Recursively extract the random variables appearing in the
        expression, and store them in a dictionary.

        :return: returns a dict with the random variables appearing in
                 the expression the keys being their names.

        :rtype: dict(string:biogeme.expressions.Expression)

        """
        return dict()

    def dictOfDraws(self):
        """Recursively extract the random variables
        (draws for Monte-Carlo).  Overloads the generic function.
        appearing in the expression, and store them in a dictionary.

        :return: dict where the keys are the random variables and
             the elements the type of draws. Here, returns an empty dict.
        :rtype: dict(string:string)
        """
        return dict()

    def getSignature(self):
        """The signature of a string characterizing an expression.

        This is designed to be communicated to C++, so that the
        expression can be reconstructed in this environment.

        The list contains the following elements:

            1. the signatures of all the children expressions,
            2. the name of the expression between < >
            3. the id of the expression between { }
            4. the number of terms in the utility ( )
            5. for each term:

                a. the id of the beta parameter
                b. the unique id of the beta parameter
                c. the name of the parameter
                d. the id of the variable
                e. the unique id of the variable
                f. the name of the variable

        Consider the following expression:

        .. math:: 2 \\beta_1  V_1 -
          \\frac{\\exp(-\\beta_2 V_2) }{ \\beta_3  (\\beta_2 \\geq \\beta_1)}.

        It is defined as::

            2 * beta1 * Variable1 - expressions.exp(-beta2*Variable2) /
                (beta3 * (beta2 >= beta1))

        And its signature is::

            [b'<Numeric>{4780527008},2',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<Times>{4780526952}(2),4780527008,4780277152',
             b'<Variable>{4511837152}"Variable1",5,2',
             b'<Times>{4780527064}(2),4780526952,4511837152',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<UnaryMinus>{4780527120}(1),4780277656',
             b'<Variable>{4511837712}"Variable2",6,3',
             b'<Times>{4780527176}(2),4780527120,4511837712',
             b'<exp>{4780527232}(1),4780527176',
             b'<Beta>{4780277264}"beta3"[1],2,0',
             b'<Beta>{4780277656}"beta2"[0],1,1',
             b'<Beta>{4780277152}"beta1"[0],0,0',
             b'<GreaterOrEqual>{4780527288}(2),4780277656,4780277152',
             b'<Times>{4780527344}(2),4780277264,4780527288',
             b'<Divide>{4780527400}(2),4780527232,4780527344',
             b'<Minus>{4780527456}(2),4780527064,4780527400']

        :return: list of the signatures of an expression and its children.
        :rtype: list(string)
        """
        listOfSignatures = []
        for e in self.children:
            listOfSignatures += e.getSignature()
        signature = f'<{self.getClassName()}>'
        signature += f'{{{id(self)}}}'
        signature += '({})'.format(len(self.listOfTerms))
        for b, v in self.listOfTerms:
            signature += (
                f',{id(b)},{b.uniqueId},{b.name},{id(v)},{v.uniqueId},{v.name}'
            )
        listOfSignatures += [signature.encode()]
        return listOfSignatures


def defineNumberingOfElementaryExpressions(
    collectionOfFormulas, variableNames
):
    """Provides indices for elementary expressions

    The numbering is done in the following order:

        (i) free betas,
        (ii) fixed betas,
        (iii) random variables for numrerical integration,
        (iv) random variables for Monte-Carlo integration,
        (v) variables

    The numbering convention will be performed for all expressions
    together, so that the same elementary expressions in several
    expressions will have the same index.

    :param collectionOfFormulas: collection of Biogeme expressions.
    :type collectionOfFormulas: list(biogeme.expressions.Expression)
    :param variableNames: list of the names of the variables
    :type variableNames: list(string)
    :return: dict, free, freeNames, fixed, fixedNames, rv, rvNames, draws,
        drawsNames where

         - dict is a dictionary mapping the names of the elementary
           expressions with their index,
         - free is a dict with the free betas,
         - freeNames is a list of the names of the free betas,
         - fixed is a dict with the fixed betas,
         - fixedNames is the list of the names of the fixed betas,
         - rv is a dict with the random variables for numerical integration,
         - rvNames is a list with their names,
         - draws is a dict of the draws, and
         - drawsNames is a list with their names.

    :rtype: tuple(dict(str: class Expression),
                  dict(str: class Beta),
                  list(str),
                  dict(str: class Beta),
                  list(str),
                  dict(str: class RandomVariable),
                  list(str),
                  dict(str: class bioDraws),
                  list(str))

    :raise biogemeError: if some elementary expressions are defined
        more than once.
    """
    # Free parameters (to be estimated), sorted by alphatical order.
    allFreeBetas = dict()
    freeBetaIndex = {}
    for f in collectionOfFormulas:
        d = f.dictOfBetas(free=True, fixed=False)
        allFreeBetas = dict(allFreeBetas, **d)
    freeBetaNames = sorted(allFreeBetas)
    #    for i in range(len(freeBetaNames)):
    for i, v in enumerate(freeBetaNames):
        freeBetaIndex[v] = i

    # Fixed parameters (not to be estimated), sorted by alphatical order.
    allFixedBetas = dict()
    fixedBetaIndex = {}
    for f in collectionOfFormulas:
        d = f.dictOfBetas(free=False, fixed=True)
        allFixedBetas = dict(allFixedBetas, **d)
    fixedBetaNames = sorted(allFixedBetas)
    #    for i in range(len(fixedBetaNames)):
    for i, v in enumerate(fixedBetaNames):
        fixedBetaIndex[v] = i

    # Random variables for numerical integration
    allRandomVariables = dict()
    randomVariableIndex = {}
    for f in collectionOfFormulas:
        d = f.dictOfRandomVariables()
        allRandomVariables = dict(allRandomVariables, **d)
    randomVariableNames = sorted(allRandomVariables)
    #    for i in range(len(randomVariableNames)):
    for i, v in enumerate(randomVariableNames):
        randomVariableIndex[v] = i

    # Draws
    allDraws = dict()
    drawIndex = {}
    for f in collectionOfFormulas:
        d = f.dictOfDraws()
        allDraws = dict(allDraws, **d)
    drawNames = sorted(allDraws)
    #    for i in range(len(drawNames)):
    for i, v in enumerate(drawNames):
        drawIndex[v] = i

    # Variables
    variableIndex = {}
    #    for i in range(len(variableNames)):
    for i, v in enumerate(variableNames):
        variableIndex[v] = i

    # Merge all the names
    allElementaryExpressions = (
        freeBetaNames
        + fixedBetaNames
        + randomVariableNames
        + drawNames
        + variableNames
    )

    if len(allElementaryExpressions) != len(set(allElementaryExpressions)):
        duplicates = {
            x
            for x in allElementaryExpressions
            if allElementaryExpressions.count(x) > 1
        }
        error_msg = (
            f'The following elementary expressions are defined '
            f'more than once: {duplicates}.'
        )
        raise excep.biogemeError(error_msg)

    elementaryExpressionIndex = {}
    for i, v in enumerate(allElementaryExpressions):
        elementaryExpressionIndex[v] = i

    for f in collectionOfFormulas:
        f.setUniqueId(elementaryExpressionIndex)
        f.setSpecificIndices(
            freeBetaIndex, fixedBetaIndex, randomVariableIndex, drawIndex
        )
        f.setVariableIndices(variableIndex)

    return (
        elementaryExpressionIndex,
        allFreeBetas,
        freeBetaNames,
        allFixedBetas,
        fixedBetaNames,
        allRandomVariables,
        randomVariableNames,
        allDraws,
        drawNames,
    )
