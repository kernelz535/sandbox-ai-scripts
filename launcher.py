import multiprocessing
import uvicorn

from app import AIP_LIST, create_app


# =====================================================
# RUN SERVER FUNCTION
# =====================================================
def run_server(app, port):
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


# =====================================================
# MAIN ENTRY POINT
# =====================================================
if __name__ == "__main__":

    processes = []

    print("\nStarting Bedrock Multi-AIP Gateway...\n")

    for aip in AIP_LIST:

        # IMPORTANT: pass port into create_app
        app = create_app(
            aip["name"],
            aip["arn"],
            aip["port"]
        )

        p = multiprocessing.Process(
            target=run_server,
            args=(app, aip["port"])
        )

        p.start()
        processes.append(p)

        print(f"Started {aip['name']} on port {aip['port']}")

    print("\nAll AIP servers are running.\n")

    # Keep parent process alive
    for p in processes:
        p.join()
