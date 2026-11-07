import argparse

from gr1naivrag.graphrag1 import naivrag, neo4j


def main() -> None:    
    parser = argparse.ArgumentParser(
        description="GraphRAG SNV futtató keretrendszer"
    )
    
    parser.add_path = parser.add_argument(
        "házi feladat",
        choices=["1", "2", "3"],
        help="Add meg, melyik házi feladat fusson: 1., 2., 3."
    )
    
    args = parser.parse_args()


    if args.feladat == "1":
        naivrag()
    elif args.feladat == "2":
        neo4j()
    elif args.feladat == "3":
        print("...")

if __name__ == "__main__":
    main()
