# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Forbidden(Exception):
    code = "FORBIDDEN"
    message = ("This action is forbidden")


class UnauthorizedException(Exception):
    code = "UNAUTHORIZED"
    message = ("You are not authorized to complete this action")


class BadRequestException(Exception):
    code = "BAD_REQUEST"
    message = ("Bad request message body")


class MalformedRequestBody(Exception):
    code = "MALFORMED_REQUEST_BODY"
    message_template = ("Malformed message body")
