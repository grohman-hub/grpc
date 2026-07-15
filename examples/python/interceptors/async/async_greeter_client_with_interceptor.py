# Copyright 2026 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Example of AsyncIO Client Interceptor usage in gRPC Python."""

import asyncio
import logging
import random

import grpc
import helloworld_pb2
import helloworld_pb2_grpc


class ClientLoggingInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """An interceptor that logs RPC requests and supports async continuation handling."""

    async def intercept_unary_unary(
        self, continuation, client_call_details, request
    ):
        print(f"[ClientInterceptor] Intercepting RPC method: {client_call_details.method}")

        # In grpc.aio, continuation can be awaited directly:
        call = await continuation(client_call_details, request)
        return call


class PassThroughClientInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """An interceptor that passes through continuation directly without explicit await.
    
    grpc.aio automatically unwraps returned coroutines so callers still only need a single await.
    """

    async def intercept_unary_unary(
        self, continuation, client_call_details, request
    ):
        print("[PassThroughInterceptor] Passing continuation through directly.")
        return continuation(client_call_details, request)


async def run() -> None:
    interceptors = [
        ClientLoggingInterceptor(),
        PassThroughClientInterceptor(),
    ]

    async with grpc.aio.insecure_channel(
        "localhost:50051", interceptors=interceptors
    ) as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        rpc_id = "{:032x}".format(random.getrandbits(128))
        metadata = grpc.aio.Metadata(
            ("client-rpc-id", rpc_id),
        )
        print(f"Sending request with rpc id: {rpc_id}")

        # Single await standard invocation
        response = await stub.SayHello(
            helloworld_pb2.HelloRequest(name="you"), metadata=metadata
        )
        print("Greeter client received: " + response.message)


if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(run())
