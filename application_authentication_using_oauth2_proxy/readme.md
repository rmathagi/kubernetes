## PURPOSE
Appplication authentication using Kubernetes, NGINX, and oAuth2. The manifest includes config to pass Token, User, Email, Groups back to the application after authetication.


## DESCRIPTION

Following Docs were referred to build the manifests:

https://github.com/oauth2-proxy/oauth2-proxy
https://oauth2-proxy.github.io/oauth2-proxy/docs
https://oak-tree.tech/blog/k8s-nginx-oauth2-gitlab

The above links already has sufficient information on how to configure and deploy a system for securing an application, We are going to look into the parameters that will be required to forward response headers back to the application.

Forward Token:
==============

Add the following parameters in oauth2-proxy deployments:

        - --set-xauthrequest=true
        - --pass-access-token=true

Add the following annotations in application ingress:

    nginx.ingress.kubernetes.io/configuration-snippet: |
      auth_request_set $token $upstream_http_x_auth_request_access_token;
      add_header 'Authorization' $token;
    nginx.ingress.kubernetes.io/proxy-buffer-size: 32k

Forward User Headers:
=====================

Add the following parameters in oauth2-proxy deployments:
        - --set-xauthrequest=true
        - --pass-user-headers=true

Add the following annotations in application ingress:

    nginx.ingress.kubernetes.io/configuration-snippet: |
      auth_request_set $user   $upstream_http_x_auth_request_user;
      auth_request_set $email  $upstream_http_x_auth_request_email;
      auth_request_set $group  $upstream_http_x_auth_request_groups;
      add_header 'X-User'  $user;
      add_header 'X-Email' $email;
      add_header 'X-Group' $group;
    nginx.ingress.kubernetes.io/proxy-buffer-size: 64k


## USAGE

$ kubectl apply -f <manifests file> 

Example Usage:

$ kubectl apply -f oauth2-proxy-deployment.yaml
deployment.apps/oauth2-proxy created
 
$ kubectl -n devops get deploy oauth2-proxy
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
oauth2-proxy   1/1     1            1           103s
