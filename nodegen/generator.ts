interface variableType {
  [className: string]: {
    filename: string;
    imports: string[];
    classes: {
      [subClassName: string]: {
        [member: string]: string;
      };
    };
  };
}

const variables: variableType = {
  Expr: {
    filename: "expression.py",
    imports: [
      "from typing import Any, List",
      "",
      "from src.pychart._interpreter.token_type import Token",
    ],
    classes: {
      Binary: {
        left: "Expr",
        operator: "Token",
        right: "Expr",
      },
      Unary: {
        operator: "Token",
        right: "Expr",
      },
      Literal: {
        value: "Any",
      },
      Grouping: {
        expr: "Expr",
      },
      Variable: {
        name: "Token",
      },
      Assignment: {
        name: "Token",
        initializer: "Expr",
      },
      Call: {
        callee: "Expr",
        arguments: "List[Expr]",
      },
    },
  },
  Stmt: {
    filename: "statement.py",
    imports: [
      "from typing import List, Optional, Any",
      "",
      "from src.pychart._interpreter.ast_nodes.expression import Expr",
      "from src.pychart._interpreter.token_type.token import Token",
    ],
    classes: {
      Expression: {
        expr: "Expr",
      },
      Print: {
        expr: "Expr",
      },
      Let: {
        name: "Token",
        initializer: "Optional[Expr]",
      },
      Block: {
        statements: "List[Stmt]",
      },
      Function: {
        name: "Token",
        params: "List[Token]",
        body: "List[Stmt]",
      },
    },
  },
};

function makeBaseClass(className: string, definition: variableType[""]) {
  return `${definition.imports.join("\n")}


class ${className}:
    def __call__(self, visitor: "${className}Visitor") -> Any:
        raise RuntimeError("Expected ${className}")

`;
}

function makeVisitorMethod(baseClassName: string, className: string) {
  return `    def ${className.toLowerCase()}(self, ${baseClassName.toLowerCase()}: "${className}") -> Any:
        ${baseClassName}Visitor.throw()`;
}

function makeVisitor(className: string, definition: variableType[""]) {
  return `
class ${className}Visitor:
    @staticmethod
    def throw():
        raise Exception("Unimplemented ${className} Visitor")

    # pylint: disable=unused-argument
${Object.entries(definition.classes)
  .map(([subClassName, _]) => makeVisitorMethod(className, subClassName))
  .join("\n\n")}

    # pylint: enable=unused-argument

`;
}

function makeSubClass(
  baseClassName: string,
  className: string,
  args: [string, string][]
) {
  return `
class ${className}(${baseClassName}):
${args.map(([field, type]) => `    ${field}: ${type}`).join("\n")}

    def __init__(self, ${args
      .map(([field, type]) => `${field}: ${type}`)
      .join(", ")}):
${args.map(([field]) => `        self.${field} = ${field}`).join("\n")}

    def __call__(self, visitor: ${baseClassName}Visitor) -> Any:
        return visitor.${className.toLowerCase()}(self)

`;
}

import * as fs from "fs";
import path from "path";

const directory = path.join(
  "..",
  "src",
  "pychart",
  "_interpreter",
  "ast_nodes"
);

Object.entries(variables).forEach(([className, definition]) => {
  let output = makeBaseClass(className, definition);
  output += makeVisitor(className, definition);

  for (let [subClassName, body] of Object.entries(definition.classes)) {
    output += makeSubClass(className, subClassName, Object.entries(body));
  }

  console.log(`/--------   ${definition.filename}   --------\\`);
  console.log(output.trim() + "\n");

  const filePath = path.join(directory, definition.filename);
  fs.writeFileSync(filePath, output);
});
